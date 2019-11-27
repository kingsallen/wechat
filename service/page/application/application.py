# coding=utf-8

import functools
import json
import re
import uuid

from tornado import gen
from tornado.escape import json_decode

import conf.common as const
import conf.message as msg
from cache.application.email_apply import EmailApplyCache
from service.page.base import PageService
from service.page.employee.employee import EmployeePageService
from service.page.user.sharechain import SharechainPageService
from util.common import ObjectDict
from util.common.mq import award_publisher
from util.tool.dict_tool import objectdictify, rename_keys
from util.tool.json_tool import json_dumps
from util.tool.iter_tool import first
from util.tool.str_tool import trunc
from util.tool.url_tool import make_static_url
from util.common.decorator import log_coro


class ApplicationPageService(PageService):

    def __init__(self):
        super().__init__()
        self.email_apply_session = EmailApplyCache()

    @log_coro(threshold=20)
    @gen.coroutine
    def get_application(self, position_id, user_id):
        """返回用户申请的职位"""

        if user_id is None:
            raise gen.Return(ObjectDict())

        ret = yield self.job_application_ds.get_job_application(conds={
            "position_id": position_id,
            "applier_id": user_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_application_by_id(self, id):
        ret = yield self.job_application_ds.get_job_application(conds={
            "id": id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_position_applied_cnt(self, conds, fields):
        """返回申请数统计"""

        response = yield self.job_application_ds.get_position_applied_cnt(
            conds=conds, fields=fields)

        raise gen.Return(response)

    @log_coro(threshold=30)
    @gen.coroutine
    def is_allowed_apply_position(self, user_id, company_id, position_id):
        """获取一个月内该用户的申请数量
        返回该用户是否可申请该职位
        reference: https://wiki.moseeker.com/application-api.md
        :param user_id: 求职者 id
        :param company_id: 公司 id
        :return:
        {
          'message': '提示信息',
          'status': 0,
          'data': true/false   # ture 表示命中限制，不能投递，false 表示可以投递
        }

        """

        if user_id is None or company_id is None or position_id is None:
            raise gen.Return(True)

        req = ObjectDict({
            'user_id': user_id,
            'company_id': company_id,
            'position_id': position_id,
        })

        ret = yield self.infra_application_ds.get_application_apply_count(req)
        bool_res = ret.data if ret.status == 0 else True

        raise gen.Return(bool_res)

    @log_coro(threshold=20)
    @gen.coroutine
    def get_application_apply_status(self, user_id, company_id):
        """
        获取求职者该公司社招校招职位是否达到投递上限
        :param user_id:
        :param company_id:
        :return: social_res:true/false, school_res:true/false  # ture 表示命中限制，不能投递，false 表示可以投递
        """
        if user_id is None or company_id is None:
            return False, False
        req = ObjectDict({
            'user_id': user_id,
            'company_id': company_id,
        })
        result, data = yield self.infra_application_ds.get_application_apply_status(req)
        if not result:
            self.logger.error('get application apply status happened some error')
            return False, False
        social_res = data.get('socialApply')
        school_res = data.get('schoolApply')
        return social_res, school_res

    @gen.coroutine
    def update_candidate_company(self, name, user_id):
        """
        更新candidate_company表中的name
        """
        res = yield self.candidate_company_ds.update_candidate_company(
            fields={"name": name},
            conds={"sys_user_id": user_id})
        raise gen.Return(res)

    @gen.coroutine
    def get_custom_tpl_all(self):
        ret = yield self.config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
            conds={'disable': const.OLD_YES},
            fields=['field_name', 'field_title', 'map']
        )
        return ret

    @gen.coroutine
    def check_custom_cv_v2(self, user_id, position_id):
        """基础服务检查改用户的简历是否符合职位的自定义简历要求"""
        params = {
            'userId': user_id,
            'positionId': position_id
        }
        result, data = yield self.infra_application_ds.custom_cv_check_v2(
            params)

        if not result:
            return False

        if data.get('resultMsg'):
            self.logger.warn(data.get('resultMsg'))

        return data.get('result', False)

    @staticmethod
    def make_fields_list(cv_conf):
        # 先将每一页的 fields 列表合并在一起，并从中剔除非必填项
        # (缩小被检查对象并将 fields 拉平成一维数组) -> fileds_to_check
        json_config = objectdictify(json_decode(cv_conf.field_value))

        def merge(x, y):
            x.extend(y)
            return x

        return functools.reduce(merge, [page.fields for page in json_config])

    @gen.coroutine
    def get_hr_app_cv_conf(self, app_cv_config_id, locale):
        cv_conf = yield self.hr_app_cv_conf_ds.get_app_cv_conf({
            "id": app_cv_config_id, "disable": const.NO
        })
        cv_conf = self.__locale_cv_conf(cv_conf, locale)
        return cv_conf

    def __locale_cv_conf(self, cv_conf, locale):
        # 国际化自定义简历模板
        if cv_conf and cv_conf.field_value:
            conf_value = json_decode(cv_conf.field_value)
            for c in conf_value:
                fields = c.get('fields')
                if fields:
                    for field in fields:
                        if field.get('field_title'):
                            field.update(field_title=locale.translate(field.get('field_title')))
                        if field.get('field_description'):
                            field.update(field_description=locale.translate(field.get('field_description')))
                        if field.get('field_value'):
                            for field_value in field.get('field_value'):
                                if isinstance(field_value, list) and field_value and field_value[0]:
                                    field_value[0] = locale.translate(field_value[0])
            cv_conf['field_value'] = json_dumps(conf_value)
            self.logger.debug("translate_cv_conf:{}".format(cv_conf))
            return cv_conf

    @gen.coroutine
    def _generate_resume_cv(self, profile, custom_tpl):
        """
        生成需要需要展示在自定义简历模版的信息:
        user_user.name 不显示,让用户自己填,
        如果没有 mobile = 0,显示空字符串
        :param profile: 基础服务提供的 profile
        :return: resume_dict
        """

        basic_other_key_mapping = {
            e.map.split('.')[1]: e.field_name for e in custom_tpl
            if e.map and e.map.startswith('profile_basic')
        }

        profile_basic = ObjectDict(profile.get("basic", {}))

        # 手机号开始
        # 没有手机号的话，mobile 为空，否则显示国家code+手机号，国家code为 86 的话不显示
        if profile_basic and not profile_basic.get("mobile"):
            profile_basic.mobile = ""
        else:
            country_code = profile_basic.get('country_code')

            profile_basic.mobile = "%s-%s" % (
                country_code or '86',
                profile_basic.get("mobile")
            )
        # 手机号结束

        # 对于 profile basic 字段自定义字段名 mapping
        rename_keys(profile_basic, basic_other_key_mapping)

        intentions = profile.get('intentions')
        if intentions:
            intention = intentions[0]
            positions = intention.get('positions')
            if positions:
                position = []
                for p in positions:
                    position.append({"position_code": p.get("position_code"), "position_name": p.get("position_name")})
                if profile_basic:
                    profile_basic.position = position
            industries = intention.get('industries')
            if industries:
                industry=[]
                for i in industries:
                    industry.append({"industry_code": i.get("industry_code"), "industry_name": i.get("industry_name")})
                if profile_basic:
                    profile_basic.industry = industry
        education = []
        for e in profile.get('educations', []):
            el = ObjectDict(
                id=e.get('id'),
                education_start=e.get('start_date', ''),
                education_end=e.get('end_date', ''),  # 可能为空
                education_end_until_now=e['end_until_now'],
                education_degree_hidden=e['degree'],
                education_major_name=e.get('major_name', ''),
                education_college_name=e.get('college_name', ''),
                education_description_hidden=e.get('description', '')
            )
            education.append(el)

        workexp = []
        for w in profile.get('workexps', []):
            el = ObjectDict(
                id=w.get('id'),
                workexp_start=w.get('start_date', ''),
                workexp_end=w.get('end_date', ''),
                workexp_end_until_now=w['end_until_now'],
                workexp_company_name=w.get('company_name', ''),
                workexp_department_name=w.get('department_name', ''),
                workexp_description_hidden=w.get('description', ''),
                workexp_job=w.get('job', ''))
            workexp.append(el)

        projectexp = []
        for p in profile.get('projectexps', []):
            el = ObjectDict(
                id=p.get('id'),
                projectexp_start=p.get('start_date', ''),
                projectexp_end=p.get('end_date', ''),
                projectexp_end_until_now=p['end_until_now'],
                projectexp_name=p.get('name', ''),
                projectexp_description_hidden=p.get('description', ''),
                projectexp_role=p.get('role', ''))
            projectexp.append(el)

        language = []
        for l in profile.get('languages', []):
            el = ObjectDict(
                id=l.get('id'),
                language_name=l.get('name', ''),
                language_level=l.get('level')
            )
            language.append(el)

        skills = []
        for s in profile.get("skills", []):
            el = ObjectDict(
                id=s.get('id'),
                skills_name=s.get('name', '')
            )
            skills.append(el)

        credentials = []
        for c in profile.get("credentials", []):
            el = ObjectDict(
                id=c.get("id"),
                credentials_name=c.get("name", "")
            )
            credentials.append(el)

        awards = []
        for a in profile.get('awards', []):
            el = ObjectDict(
                id=a.get('id'),
                awards_reward_date=a.get('reward_date', ''),
                awards_name=a.get('name', ''))
            awards.append(el)

        works = []
        for w in profile.get('works', []):
            el = ObjectDict(
                id=w.get('id'),
                works_cover=make_static_url(w.get('cover')) if w.get('cover') else None,
                works_url=w.get('url', ''),
                works_description=w.get('description', ''))
            works.append(el)

        resume_dict = ObjectDict(profile_basic)
        resume_dict.education = education
        resume_dict.workexp = workexp
        resume_dict.projectexp = projectexp
        resume_dict.awards = awards
        resume_dict.works = works
        resume_dict.skills = skills
        resume_dict.credentials = credentials
        resume_dict.language = language

        # profile other
        if profile.get('others', []):
            other_string = first(profile.get('others')).get('other', '{}')
            resume_dict.update(json.loads(other_string))

        return resume_dict

    @gen.coroutine
    def get_profile_other(self, profile_id):
        result, data = yield self.infra_profile_ds.get_profile_other(
            profile_id)
        if result:
            return ObjectDict(json_decode(data[0]['other']))
        else:
            return ObjectDict()

    @gen.coroutine
    def bind_app_chain_info(self, app_id, psc_id, direct_referral_user_id):
        params = ObjectDict({
            "application_id": app_id,
            "psc_id": psc_id or 0,
            "direct_referral_user_id": direct_referral_user_id or 0
        })
        yield self.infra_application_ds.bind_apply_chain_info(params)

    @gen.coroutine
    def update_profile_other(self, new_record, profile_id):
        """智能地更新 profile.other 表
        会主动 merge 已经有的自定义字段
        """

        old_profile_other_record = yield self.profile_other_ds.get_profile_other(conds={
            'profile_id': profile_id
        })

        self.logger.debug("[profile_other] old_profile_other_record: %s" % old_profile_other_record)

        if old_profile_other_record:
            old_other = old_profile_other_record.other
            old_other_dict = json_decode(old_other)

            self.logger.debug("[profile_other] old_other_dict: %s" % old_other_dict)

            new_other_dict = json_decode(new_record.other)

            self.logger.debug("[profile_other] new_other_dict: %s" % new_other_dict)

            # 需对 picUrl 做特殊处理
            new_other_dict.pop('picUrl', None)

            old_other_dict.update(new_other_dict)
            other_dict_to_update = old_other_dict

            self.logger.debug("[profile_other] other_dict_to_update: %s" % other_dict_to_update)

            params = {
                'other': json_dumps(other_dict_to_update),
                'profile_id': profile_id
            }

            result, data = yield self.infra_profile_ds.update_profile_other(
                params)

        else:
            self.logger.debug("[profile_other] new_record: %s" % new_record)

            # 转换一下 new_record 中 utf-8 char
            new_record = ObjectDict(new_record)
            other_str = new_record.other

            other_dict = json.loads(other_str)
            other_dict.pop('picUrl', None)

            new_record.other = json_dumps(other_dict)
            params = new_record

            result, data = yield self.infra_profile_ds.create_profile_other(
                params, profile_id)

        return result

    @gen.coroutine
    def create_email_apply(self, params, position, current_user, is_platform=True, source=None):
        """ 创建Email申请
        :param params:
        :param position:
        :param current_user:
        :param is_platform:
        :param source:
        :return:
        """

        check_status, message = yield self.check_position(position, current_user)
        self.logger.debug(
            "[create_email_reply]check_status:{}, message:{}".format(
                check_status, message))
        if not check_status:
            raise gen.Return((False, message))

        # 获取推荐人信息
        recommender_user_id, recommender_wxuser_id, recom_employee, depth = yield self.get_recommend_user(
            current_user, position, is_platform)

        # if source == const.REHIRING_SOURCE:
        #     origin = const.REHIRING_ORIGIN
        if current_user.employee and current_user.company.id in const.TRANSFER_COMPANY_ID:
            origin = const.TRANSFER_ORIGIN
        elif params.invite_apply == str(const.YES):
            origin = const.INVITE_ORIGIN
        else:
            origin = 2 if is_platform else 4

        params_for_application = ObjectDict(
            wechat_id=current_user.wechat.id,
            position_id=position.id,
            recommender_id=recommender_wxuser_id,
            recommender_user_id=recommender_user_id,
            applier_id=current_user.sysuser.id,
            company_id=position.company_id,
            routine=0 if is_platform else 1,
            apply_type=1,  # 投递区分， 0：profile投递， 1：email投递
            email_status=1,
            # email解析状态: 0，有效；1,未收到回复邮件；2，文件格式不支持；3，附件超过10M；9，提取邮件失败
            origin=origin
        )

        ret = yield self.infra_application_ds.create_application(params_for_application)

        # 申请创建失败,  跳转到申请失败页面
        if not ret.status == const.API_SUCCESS:
            message = ret.message
            return False, message

        uuidcode = str(uuid.uuid4())
        email_params = ObjectDict(
            email_address=params.email,
            company_abbr=current_user.company.abbreviation or current_user.company.name,
            applier_name=params.name or current_user.sysuser.name,
            invitation_code=uuidcode,
            plat_type=1 if is_platform else 2
        )
        if is_platform:
            # 如果是platform的话, 都是KA用户, 需要以下额外的信息
            email_params_wechat_info = dict(
                company_logo=current_user.company.logo,
                official_account_name=current_user.wechat.name,
                official_account_qrcode=current_user.wechat.qrcode
            )
            email_params.update(email_params_wechat_info)

        # 将部分申请信息存入redis, 解析邮件脚本使用.
        value_dict = ObjectDict(
            user_id=current_user.sysuser.id,
            curr_wxuser_id=current_user.wxuser.id or 0,
            mobile=current_user.sysuser.mobile,
            app_id=ret.data.jobApplicationId,
            last_employee_recom_user_id=recommender_user_id,
            last_employee_recom_id=recommender_wxuser_id,
            project=is_platform,
            reply_email_info=email_params
        )

        self.email_apply_session.save_email_apply_sessions(uuidcode, value_dict)
        rst = yield self.opt_send_email_create_application_notice(email_params)

        raise gen.Return((True, None))

    @gen.coroutine
    def check_position(self, position, current_user):
        """
        职位验证，包含是否含有职位，职位是否过期，是否可以申请的验证
        :param position:
        :param current_user:
        :return:
        """
        is_ok = True
        message = ''

        # 职位是否过期
        if position.status != const.OLD_YES:
            message = msg.POSITION_ALREADY_EXPIRED
            is_ok = False

        # 判断当前职位是否提交过？
        application = yield self.get_application(
            position.id, current_user.sysuser.id)

        if application:
            message = msg.DUPLICATE_APPLICATION
            is_ok = False

        return is_ok, message

    @gen.coroutine
    def create_email_profile(self, params, current_user, is_platform=True):
        """
        只是创建创建Email Profile 不包含申请
        将部分申请信息存入redis, 解析邮件脚本使用.
        :param params:
        :param current_user:
        :param is_platform:
        :return:
        """

        uuidcode = str(uuid.uuid4())

        email_params = ObjectDict(
            email_address=params.email,
            applier_name=params.name or current_user.sysuser.name,
            invitation_code=uuidcode,
            plat_type=1 if is_platform else 2
        )
        value_dict = ObjectDict(
            user_id=current_user.sysuser.id,
            curr_wxuser_id=current_user.wxuser.id or 0,
            mobile=current_user.sysuser.mobile,
            project=is_platform,
            reply_email_info=email_params
        )

        self.email_apply_session.save_email_apply_sessions(uuidcode,
                                                           value_dict)
        self.logger.debug(
            "[create_email_profile]value_dict:{}".format(value_dict))
        # 求职者发送Email创建邮件
        yield self.opt_send_email_create_profile_notice(email_params)

    def __split_dot(self, p_str):
        """
        内部方法,不要无故使用
        """
        if p_str.find(".") > 0:
            r_ret = p_str.split(".")
            if len(r_ret) == 2:
                return tuple(r_ret)
        return None

    @gen.coroutine
    def create_application(self, position, current_user, params,
                           is_platform=True, has_recom=False, source=None):

        # 1.初始化
        check_status, message = yield self.check_position(position, current_user)

        if not check_status:
            return False, message, None

        # 2.创建申请
        if has_recom:
            recommender_user_id, recommender_wxuser_id, recom_employee, depth = \
                yield self.get_recommend_user(current_user, position, is_platform)
        else:
            recommender_user_id, recommender_wxuser_id, recom_employee = 0, 0, None

        # if source == const.REHIRING_SOURCE:
        #     origin = const.REHIRING_ORIGIN
        if current_user.employee and current_user.company.id in const.TRANSFER_COMPANY_ID:
            origin = const.TRANSFER_ORIGIN
        elif params.invite_apply == str(const.YES):
            origin = const.INVITE_ORIGIN
        else:
            origin = 2 if is_platform else 4

        params_for_application = ObjectDict(
            position_id=position.id,
            recommender_id=recommender_wxuser_id,
            recommender_user_id=recommender_user_id,
            applier_id=current_user.sysuser.id,
            company_id=position.company_id,
            origin=origin  # 2 -> 企业号申请， 4 -> 聚合号申请
        )
        self.logger.debug("params_for_application: {}".format(
            params_for_application))

        ret = yield self.infra_application_ds.create_application(
            params_for_application)

        if ret.status != const.API_SUCCESS:
            return False, ret.message, 0

        apply_id = ret.data.jobApplicationId

        return True, msg.RESPONSE_SUCCESS, apply_id

    @gen.coroutine
    def get_recommend_user(self, current_user, position, is_platform):

        self.logger.debug("[get_recommend_user]start")
        recommender_user_id = 0
        recommender_wxuser_id = 0
        depth = 0
        recom_employee = ObjectDict()
        sharechain_ps = SharechainPageService()

        if is_platform:
            recommender_user_id, depth = yield sharechain_ps.get_referral_employee_user_id(
                current_user.sysuser.id, position.id)

            if recommender_user_id:
                recom_employee = yield self.user_employee_ds.get_employee(conds={
                    "sysuser_id": current_user.sysuser.id,
                    "disable": const.NO,
                    "activation": const.NO,
                })
                recommender_wxuser_id = recom_employee.wxuser_id or 0

        sharechain_ps = None
        self.logger.debug("[get_recommend_user]end")
        return recommender_user_id, recommender_wxuser_id, recom_employee, depth

    @gen.coroutine
    def opt_add_reward(self, apply_id, current_user):
        """ 申请添加积分 """

        self.logger.debug("[opt_add_reward]start")

        application = yield self.get_application_by_id(apply_id)
        if not application or not application.recommender_user_id:
            return

        recommender_user_id = application.recommender_user_id

        if recommender_user_id:
            recommender_employee_id = 0
            employee_ps = EmployeePageService()
            _, employee_info = yield employee_ps.get_employee_info(
                user_id=recommender_user_id,
                company_id=current_user.company.id
            )
            if employee_info:
                recommender_employee_id = employee_info.id

            award_publisher.add_awards_apply(
                company_id=application.company_id,
                position_id=application.position_id,
                employee_id=recommender_employee_id,
                recom_user_id=recommender_user_id,
                be_recom_user_id=current_user.sysuser.id,
                application_id=apply_id
            )

        self.logger.debug("[opt_add_reward]end")

    @gen.coroutine
    def opt_update_candidate_recom_records(self, apply_id, current_user,
                                           recommend_user_id, position):
        """
        更新挖掘被动求职者相关信息
        :param apply_id:
        :param current_user:
        :param recommend_user_id:
        :param position:
        :return:
        """
        self.logger.debug("[opt_update_candidate_recom_records]start")
        if current_user.wechat.passive_seeker == const.OLD_YES and recommend_user_id:
            yield self.candidate_recom_record_ds.update_candidate_recom_record(
                conds={
                    "position_id": position.id,
                    "post_user_id": recommend_user_id,
                    "presentee_user_id": current_user.sysuser.id,
                }, fields={
                    "app_id": apply_id
                }
            )
        self.logger.debug("[opt_update_candidate_recom_records]end")

    @gen.coroutine
    def opt_send_email_create_application_notice(self, email_params):
        """向求职者发送创建 email 申请邮件"""

        to_email = email_params["email_address"]
        company_abbr = email_params["company_abbr"]
        applier_name = email_params["applier_name"]
        invitation_code = email_params["invitation_code"]
        plat_type = email_params["plat_type"]

        if plat_type == 2:
            # 2是qx, 不管是不是KA, 都是以仟寻名义发送
            template_name = const.NON_KA_EMAIL_APPLICATION_INVITATION
            from_email = self.settings.cv_mail_sender_email
            merge_vars = ObjectDict(
                company_abbr=company_abbr,
                header_company_abbr=trunc(company_abbr, const.MANDRILL_EMAIL_HEADER_LIMIT),
                applier_name=applier_name,
                header_applier_name=trunc(applier_name, const.MANDRILL_EMAIL_HEADER_LIMIT),
                invitation_code=invitation_code
            )
        else:
            # 1是platform, 都是KA, 以公司的名义发送
            template_name = const.KA_EMAIL_APPLICATION_INVITATION
            from_email = self.settings.cv_mail_sender_email
            merge_vars = ObjectDict(
                company_abbr=company_abbr,
                header_company_abbr=trunc(company_abbr, const.MANDRILL_EMAIL_HEADER_LIMIT),
                applier_name=applier_name,
                header_applier_name=trunc(applier_name, const.MANDRILL_EMAIL_HEADER_LIMIT),
                invitation_code=invitation_code,
                company_logo=email_params['company_logo'],
                official_account_name=email_params['official_account_name'],
                official_account_qrcode=email_params['official_account_qrcode']
            )

        yield self.thrift_mq_ds.send_mandrill_email(template_name, to_email, "", from_email, "", "", merge_vars)

    @gen.coroutine
    def opt_send_email_create_profile_notice(self, email_params):
        """向求职者发送创建 profile 邮件"""

        to_email = email_params["email_address"]
        applier_name = email_params["applier_name"]
        invitation_code = email_params["invitation_code"]

        template_name = "email-profile-creation-invitation"
        from_email = self.settings.cv_mail_sender_email
        merge_vars = ObjectDict(
            applier_name=applier_name,
            header_applier_name=trunc(applier_name, const.MANDRILL_EMAIL_HEADER_LIMIT),
            invitation_code=invitation_code,
        )

        yield self.thrift_mq_ds.send_mandrill_email(template_name, to_email, "", from_email, "", "", merge_vars)

    def custom_fields_need_kvmapping(self, config_cv_tpls):
        """ 工具方法，
        查找 config_cv_tpls 表中值为字典值的数据，
        然后组合成如下数据结构：(截止至 2017-03-24)
        {
            'AddressProvince':       {
                'title': '地址所在省/直辖市',
                'value': {'0':  '',
                          '1':  '安徽省',
                          '10': '海南省',
                          '11': '河北省',
                          '12': '河南省',
                          '13': '黑龙江省',
                          '14': '湖北省',
                          '15': '湖南省',
                          '16': '吉林省',
                          '17': '江苏省',
                          '18': '江西省',
                          '19': '辽宁省',
                          '2':  '澳门',
                          '20': '内蒙古自治区',
                          '21': '宁夏回族自治区',
                          '22': '青海省',
                          '23': '山东省',
                          '24': '山西省',
                          '25': '陕西省',
                          '26': '上海',
                          '27': '四川省',
                          '28': '天津',
                          '29': '台湾省',
                          '3':  '北京',
                          '30': '香港',
                          '31': '西藏自治区',
                          '32': '新疆省',
                          '33': '浙江省',
                          '34': '云南省',
                          '4':  '重庆',
                          '5':  '福建省',
                          '6':  '甘肃省',
                          '7':  '广东省',
                          '8':  '广西省',
                          '9':  '贵州省'}},
            'ExpectedInterviewCity': {'title': '期望面试城市',
                                      'value': {'0': '',
                                                '1': '哈尔滨',
                                                '2': '沈阳',
                                                '3': '石家庄',
                                                '4': '重庆',
                                                '5': '青岛',
                                                '6': '济南',
                                                '7': '无锡',
                                                '8': '郑州',
                                                '9': '开封'}},
            'InterestedJobFunction': {'title': ' 感兴趣职能',
                                      'value': {'0':  '',
                                                '1':  '行政管理',
                                                '10': '市场营销',
                                                '11': '生产制造',
                                                '12': '采购',
                                                '13': '研发',
                                                '14': '销售',
                                                '15': '供应链计划/物流',
                                                '16': '宠物医院服务',
                                                '17': '动物医学',
                                                '18': '兽医师（未持证）',
                                                '19': '职业技术/技工',
                                                '2':  '企业事务/公共关系',
                                                '20': '培训生项目',
                                                '21': '实习生',
                                                '3':  '法律/合规',
                                                '4':  '执业兽医师',
                                                '5':  '工程/机械',
                                                '6':  '财务',
                                                '7':  '医疗护理',
                                                '8':  '人力资源',
                                                '9':  'IT信息技术'}},
            'InterestingExtent':     {'title': '感兴趣程度',
                                      'value': {'0': '',
                                                '1': '暂不考虑新的工作机会',
                                                '2': '随意浏览，了解工作机会',
                                                '3': '积极求职，目前处于在职状态',
                                                '4': '可以立即入职'}},
            'IsFreshGraduated':      {'title': '应届/往届',
                                      'value': {'0': '', '1': '应届',
                                                '2': '往届'}},
            'JapaneseLevel':         {'title': '日语等级',
                                      'value': {'0': '',
                                                '1': '一级',
                                                '2': '二级',
                                                '3': '三级',
                                                '4': '四级',
                                                '5': '未通过'}},
            'PoliticalStatus':       {'title': '政治面貌',
                                      'value': {'0': '',
                                                '1': '中共党员(含预备党员)',
                                                '2': '团员',
                                                '3': '群众'}},
            'cpa':                   {'title': 'CPA证书',
                                      'value': {'0': '', '1': '有CPA',
                                                '2': '无CPA'}},
            'degree':                {'title': '学历',
                                      'value': {'0': '',
                                                '1': '大专以下',
                                                '2': '大专',
                                                '3': '本科',
                                                '4': '硕士',
                                                '5': '博士',
                                                '6': '博士以上'}},
            'expectsalary':          {'title': '期望年薪',
                                      'value': {'0': '',
                                                '1': '6万以下',
                                                '2': '6万-8万',
                                                '3': '8万-12万',
                                                '4': '12-20万',
                                                '5': '20万-30万',
                                                '6': '30万以上'}},
            'frequency':             {'title': '选择班次',
                                      'value': {'0': '', '1': '早', '2': '中',
                                                '3': '晚'}},
            'gender':                {'title': '性别',
                                      'value': {'0': '', '1': '男', '2': '女'}},
            'icanstart':             {'title': '到岗时间',
                                      'value': {'0': '',
                                                '1': '随时',
                                                '2': '两周',
                                                '3': '一个月',
                                                '4': '一个月以上'}},
            'industry':              {'title': '期望行业',
                                      'value': {'0':  '',
                                                '1':  '计算机/通信/电子/互联网',
                                                '10': '服务业',
                                                '11': '文化/传媒/娱乐/体育',
                                                '12': '能源/矿产/环保',
                                                '13': '政府/非盈利机构/其他',
                                                '2':  '会计/金融/银行/保险',
                                                '3':  '房地产/建筑业',
                                                '4':  '商业服务/教育/培训',
                                                '5':  '贸易/批发/零售/租赁业',
                                                '6':  '制药/医疗',
                                                '7':  '广告/媒体',
                                                '8':  '生产/加工/制造',
                                                '9':  '交通/运输/物流/仓储'}},
            'majorrank':             {'title': '专业排名',
                                      'value': {'0': '',
                                                '1': '5%',
                                                '2': '5%—15%',
                                                '3': '15%-30%',
                                                '4': '30%-50%',
                                                '5': '50%以下'}},
            'marriage':              {'title': '婚姻状况',
                                      'value': {'0': '', '1': '未婚',
                                                '2': '已婚'}},
            'nightjob':              {'title': '是否接受夜班',
                                      'value': {'0': '', '1': '接受',
                                                '2': '不接受'}},
            'residencetype':         {'title': '户口类型',
                                      'value': {'0': '', '1': '农业户口',
                                                '2': '非农业户口'}},
            'salary':                {'title': '当前年薪',
                                      'value': {'0': '',
                                                '1': '6万以下',
                                                '2': '6万-8万',
                                                '3': '8万-12万',
                                                '4': '12-20万',
                                                '5': '20万-30万',
                                                '6': '30万以上'}},
            'servedoffice':          {'title': '曾供职事务所',
                                      'value': {'0': '',
                                                '1': 'KPMG',
                                                '2': 'Deloitte',
                                                '3': 'PWC',
                                                '4': 'EY',
                                                '5': '其他'}},
            'trip':                  {'title': '是否接受长期出差',
                                      'value': {'0': '', '1': '接受',
                                                '2': '不接受'}},
            'workdays':              {'title': '每周到岗天数(实习)',
                                      'value': {'0': '',
                                                '1': '1天/周',
                                                '2': '2天/周',
                                                '3': '3天/周',
                                                '4': '4天/周',
                                                '5': '5天/周'}},
            'workstate':             {'title': '工作状态',
                                      'value': {'0': '',
                                                '1': '在职，看看新机会',
                                                '2': '在职，急寻新工作',
                                                '3': '在职，暂无跳槽打算',
                                                '4': '离职，正在找工作',
                                                '5': '应届毕业生'}}}
        :param config_cv_tpls:
        :return:
        """

        # 有 kv mapping 的字段
        records = [ObjectDict(r) for r in config_cv_tpls]
        kvmappinp_ret = ObjectDict()
        for record in records:
            value = {}
            if record.field_value:
                value_list = re.split(',|:', record.field_value)

                len_value_list = len(value_list)
                for i in range(int(len_value_list / 2)):
                    i_value = i * 2
                    i_key = i_value + 1

                    if value_list[i_value] and value_list[i_key]:
                        value.update({value_list[i_key]: value_list[i_value]})

                value.update({'0': ''})

            kvmappinp_ret.update({
                record.field_name: {
                    "title": record.field_title,
                    "value": value}
            })

        self.logger.info(kvmappinp_ret)
        return kvmappinp_ret
