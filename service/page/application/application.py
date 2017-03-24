# coding=utf-8

import os
import functools
import uuid

from tornado import gen
from tornado.escape import json_decode, json_encode

import conf.common as const
import conf.message as msg
import conf.path as path
from cache.application.email_apply import EmailApplyCache
from service.page.base import PageService
from service.page.user.sharechain import SharechainPageService
from service.page.user.profile import ProfilePageService
from util.common.subprocess import Sub
from util.common import ObjectDict
from util.tool.json_tool import json_dumps
from util.tool.str_tool import trunc
from util.tool.url_tool import make_url
from util.tool.dict_tool import objectdictify
from util.tool.pdf_tool import save_application_file, get_create_pdf_by_html_cmd
from util.tool.mail_tool import send_mail_notice_hr
from util.wechat.template import application_notice_to_applier_tpl, application_notice_to_recommender_tpl, application_notice_to_hr_tpl
from thrift_gen.gen.mq.struct.ttypes import SmsType


class ApplicationPageService(PageService):
    def __init__(self):
        super().__init__()
        self.email_apply_session = EmailApplyCache()

    @gen.coroutine
    def get_application(self, position_id, user_id):
        """返回用户申请的职位"""

        if user_id is None:
            raise gen.Return(ObjectDict())

        ret = yield self.job_application_ds.get_job_application(conds={
            "position_id": position_id,
            "applier_id":  user_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_position_applied_cnt(self, conds, fields):
        """返回申请数统计"""

        response = yield self.job_application_ds.get_position_applied_cnt(
            conds=conds, fields=fields)

        raise gen.Return(response)

    @gen.coroutine
    def is_allowed_apply_position(self, user_id, company_id):
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

        if user_id is None or company_id is None:
            raise gen.Return(True)

        req = ObjectDict({
            'user_id':    user_id,
            'company_id': company_id,
        })

        ret = yield self.infra_application_ds.get_application_apply_count(req)
        bool_res = ret.data if ret.status == 0 else True

        raise gen.Return(bool_res)

    @gen.coroutine
    def update_candidate_company(self, name, user_id):
        """
        更新candidate_company表中的name
        :param user_id:
        :return:
        """

        res = yield self.candidate_company_ds.update_candidate_company(
            fields={
                "sys_user_id": user_id
            }, conds={
                "name": name,
            })
        raise gen.Return(res)

    @gen.coroutine
    def check_custom_cv(self, current_user, position, custom_tpls):
        """ 处理自定义简历校验和失败后的跳转
        如果校验失败，handler（调用方）需要立即 return
        """
        profile = current_user.profile
        user = current_user.sysuser

        cv_conf = yield self.get_hr_app_cv_conf(position.app_cv_config_id)
        fields = self.make_fields_list(cv_conf)
        fileds_to_check = [f for f in objectdictify(fields) if f.required == const.OLD_YES]

        # 对于 fileds_to_check 进行逐个检查
        # 校验失败条件:
        # field_name 在 profile 对应字端中,但是 profile 中这个字段为空值
        # or
        # field_name 是纯自定义字段,但是在 custom_others 中没有这个值
        for field in fileds_to_check:
            field_name = field.field_name
            mapping = field.map
            passed = yield self._check(profile, field_name, user, mapping)

            if not passed:
                self.logger.debug("自定义字段必填校验错误, field_name: %s" % field_name)
                resume_dict = yield self._generate_resume_cv(profile)
                self.logger.debug("resume_dict: %s" % resume_dict)
                return (False, resume_dict, objectdictify(json_decode(cv_conf.field_value)))
        return True, None, None

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
    def get_hr_app_cv_conf(self, app_cv_config_id):
        cv_conf = yield self.hr_app_cv_conf_ds.get_app_cv_conf({
            "id": app_cv_config_id, "disable": const.NO
        })
        return cv_conf

    @gen.coroutine
    def _check(self, profile, field_name, user, mapping):
        """检查自定义字段必填项"""

        # 如果 filed 是 profile 字段
        if mapping:
            return self._check_profile_fields(profile, field_name, user, mapping)

        # 如果 field 是纯自定义字段
        else:
            ret = yield self._check_custom_fields(profile, field_name, mapping)
            return ret

        assert False  # should not be here

    def _check_profile_fields(self, profile, field_name, user, mapping):
        self.logger.debug("field_name: %s" % field_name)

        if mapping.startswith("user_user"):
            sysuser_id = profile.get("profile", {}).get("user_id", None)
            if not sysuser_id:
                return False

            column_name = mapping.split(".")[1]
            self.logger.debug(
                "sysuser_id: %s, column_name: %s" % (sysuser_id, column_name))

            if column_name not in ['email', 'name', 'mobile', 'headimg']:
                return False
            else:
                return bool(getattr(user, column_name))

        if mapping.startswith("profile_education"):
            return bool(profile.get('educations', []))

        if mapping.startswith("profile_workexp"):
            return bool(profile.get('workexps', []))

        if mapping.startswith("profile_projectexp"):
            return bool(profile.get('projectexps', []))

        if mapping.startswith("profile_basic"):
            table_name, column_name = self._split_dot(mapping)
            if table_name:
                key_1 = table_name.split("_")[1]  # should be "basic"
                key_2 = column_name
                return bool(profile.get(key_1, {}).get(key_2, None))
            else:
                return False

        assert False  # should not be here

    @staticmethod
    def _split_dot(p_str):
        if p_str.find(".") > 0:
            r_ret = p_str.split(".")
            return r_ret[0], r_ret[1]
        return None, None

    @gen.coroutine
    def _check_custom_fields(self, profile, field_name, mapping):
        profile_id = profile.profile.id
        other = yield self.get_profile_other(profile_id)

        if not other:
            return False
        else:
            self.logger.debug("other: %s" % other)
            return bool(getattr(other, field_name))

    @gen.coroutine
    def _generate_resume_cv(self, profile):
        """
        生成需要需要展示在自定义简历模版的信息:
        user_user.name 不显示,让用户自己填,
        如果没有 mobile = 0,显示空字符串
        :param profile: 基础服务提供的 profile
        :return: resume_dict
        """
        profile_basic = ObjectDict(profile.get("basic", None))
        if profile_basic and not profile_basic.get("mobile"):
            profile_basic.mobile = ""
        profile_basic.name = ""
        degree_list = yield self.infra_dict_ds.get_const_dict(
            const.CONSTANT_PARENT_CODE.DEGREE_USER)

        education = []
        for e in profile.get('educations'):
            __end = u'至今' if e.get('end_until_now', False) \
                else e.get('end_date', '')
            end = __end
            __start = e.get('start_date', '')
            start = __start
            degree = e.get('degree')
            _degree = degree_list.get(str(degree))
            major = e.get('major_name')
            school = e.get('college_name')

            el = ObjectDict(
                id=e.get('id'),
                __end=__end,
                end=end,
                __start=__start,
                start=start,
                end_until_now=1 if end == u"至今" else 0,
                _degree=_degree,
                degree=degree,
                major=major,
                school=school)
            education.append(el)

        workexp = []
        for w in profile.get('workexps'):
            __end = u'至今' if w.get('end_until_now', False) \
                else w.get('end_date', '')
            end = __end
            __start = w.get('start_date', '')
            start = __start
            company = w.get('company_name')
            department = w.get('department_name')
            describe = w.get('description')
            position = w.get('position_name')
            el = ObjectDict(
                id=w.get('id'),
                __end=__end,
                end=end,
                __start=__start,
                start=start,
                end_until_now=1 if end == u"至今" else 0,
                company=company,
                department=department,
                describe=describe,
                position=position)
            workexp.append(el)

        projectexp = []
        for p in profile.get('projectexps'):
            __end = u'至今' if p.get('end_until_now', False) \
                else p.get('end_date', '')
            end = __end
            __start = p.get('start_date', '')
            start = __start
            name = p.get('name')
            introduce = p.get('description')
            role = p.get('responsibility')
            position = p.get('role')
            el = ObjectDict(
                id=p.get('id'),
                __end=__end,
                end=end,
                __start=__start,
                start=start,
                end_until_now=1 if __end == u"至今" else 0,
                name=name,
                introduce=introduce,
                role=role,
                position=position)
            projectexp.append(el)

        resume_dict = ObjectDict(profile_basic)
        resume_dict.education = education
        resume_dict.workexp = workexp
        resume_dict.projectexp = projectexp

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
    def update_profile_other(self, new_record, profile_id):
        old_other = yield self.get_profile_other(profile_id)

        # Sample:
        # new_record: {'other': '{"nationality": "\\u4e2d\\u56fd 123", "height": "177"}'}
        # old_other: {'nationality': '中国', 'height': '177'}

        if old_other:
            new_other_dict = json_decode(new_record.other)
            old_other.update(new_other_dict)
            other_dict_to_update = old_other
            params = {
                'other': json_dumps(other_dict_to_update),
                'profile_id': profile_id
            }
            result, data = yield self.infra_profile_ds.update_profile_other(params)

        else:
            # 转换一下 new_record 中 utf-8 char
            new_record = ObjectDict(new_record)
            new_record.other = json_dumps(json_decode(new_record.other))
            record_to_update = new_record

            result, data = yield self.infra_profile_ds.create_profile_other(
                record_to_update, profile_id)

        return result

    @gen.coroutine
    def save_job_resume_other(self, profile, app_id, position):
        """申请成功后将 profile other 的对应字段保存到 job_resume_other
        :param profile: 全profile
        :param app_id:  申请id
        :param position: 申请职位
        :return: (result, message)
        """
        if not position.app_cv_config_id:
            return True, None

        resume_other = ObjectDict()

        cv_conf = yield self.get_hr_app_cv_conf(position.app_cv_config_id)
        fields = self.make_fields_list(cv_conf)
        p_other = profile.others

        for field in fields:
            if p_other.get(field):
                resume_other.update({field: p_other.get(field)})
        resume_other_to_insert = json_encode(resume_other, ensure_ascii=False)
        self.logger.debug('resume_other_to_insert: %s' % resume_other_to_insert)
        yield self.hr_resume_other_ds.insert_job_resume_other({
            'appid': app_id,
            'other': resume_other_to_insert
        })
        return True, None

    @gen.coroutine
    def create_email_apply(self, params, position, current_user, is_platform=True):
        """ 创建Email申请
        :param params:
        :param position:
        :param current_user:
        :param is_platform:
        :return:
        """

        check_status, message = self.check_position(position, current_user)
        self.logger.debug(
            "[create_email_reply]check_status:{}, message:{}".format(
                check_status, message))
        if not check_status:
            raise gen.Return((False, message))

        # 获取推荐人信息
        recommender_user_id, recommender_wxuser_id, recom_employee = yield self.get_recommend_user(
            current_user, position, is_platform)

        self.logger.debug("[create_email_reply]recommender_user_id:{}, recommender_wxuser_id:{}".format(recommender_user_id, recommender_wxuser_id))

        params_for_application = ObjectDict(
            wechat_id=current_user.wechat.id,
            position_id=position.id,
            recommender_id=recommender_wxuser_id,
            recommender_user_id=recommender_user_id,
            applier_id=current_user.sysuser.id,
            company_id=position.company_id,
            routine=0 if is_platform else 1,
            apply_type=1,  # 投递区分， 0：profile投递， 1：email投递
            email_status=1
            # email解析状态: 0，有效；1,未收到回复邮件；2，文件格式不支持；3，附件超过10M；9，提取邮件失败
        )

        self.logger.debug("[create_email_reply]params_for_application:{}".format(recommender_wxuser_id))

        ret = yield self.infra_application_ds.create_application(params_for_application)

        # 申请创建失败,  跳转到申请失败页面
        if not ret.status != const.API_SUCCESS:
            message = msg.CREATE_APPLICATION_FAILED
            raise gen.Return((False, message))

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

        self.logger.debug(
            "[create_email_reply]value_dict:{}".format(value_dict))

        self.email_apply_session.save_email_apply_sessions(uuidcode, value_dict)
        rst = yield self.opt_send_email_create_application_notice(email_params)
        self.logger.debug("[create_email_reply]Send Email to creator " + str(rst))

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

        # 判断当前用户手机号
        if str(current_user.sysuser.mobile) != str(
            current_user.sysuser.username):
            message = msg.CELLPHONE_MOBILE_INVALID
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
    def create_application(self, position, current_user,
                           is_platform=True):

        # 1.初始化
        check_status, message = yield self.check_position(position, current_user)
        self.logger.debug(
            "[create_reply]check_status:{}, message:{}"
            .format(check_status, message))

        if not check_status:
            return False, message, None

        # 2.创建申请
        recommender_user_id, recommender_wxuser_id, recom_employee = \
            yield self.get_recommend_user(current_user, position, is_platform)

        params_for_application = ObjectDict(
            position_id=position.id,
            recommender_id=recommender_wxuser_id,
            recommender_user_id=recommender_user_id,
            applier_id=current_user.sysuser.id,
            company_id=position.company_id,
            routine=0 if is_platform else 1
        )
        self.logger.debug("params_for_application: {}".format(
            params_for_application))

        ret = yield self.infra_application_ds.create_application(
            params_for_application)

        if ret.status != const.API_SUCCESS:
            return False, msg.CREATE_APPLICATION_FAILED

        apply_id = ret.data.jobApplicationId

        # 申请的后续处理
        self.logger.debug("[post_apply]投递后续处理")

        #1. 添加积分
        yield self.opt_add_reward(apply_id, current_user, position, is_platform)
        #2. 向求职者发送消息通知（消息模板，短信）
        yield self.opt_send_applier_msg(apply_id, current_user, position, is_platform)
        #3. 向推荐人发送消息模板
        yield self.opt_send_recommender_msg(recommender_user_id, current_user, position, current_user.profile)
        #4. 更新挖掘被动求职者信息
        yield self.opt_update_candidate_recom_records(apply_id, current_user, recommender_user_id, position)
        #5. 向 HR 发送消息通知（消息模板，短信，邮件）
        yield self.opt_hr_msg(apply_id, current_user, current_user.profile, position, is_platform)

        # TODO (tangyiliang) 发红包
        # yield self.opt_send_redpacket(current_user, position)

        return True, msg.RESPONSE_SUCCESS, apply_id

    @gen.coroutine
    def get_recommend_user(self, current_user, position, is_platform):

        self.logger.debug("[get_recommend_user]start")
        recommender_user_id = 0
        recommender_wxuser_id = 0
        recom_employee = ObjectDict()
        sharechain_ps = SharechainPageService()

        if is_platform:
            recommender_user_id = yield sharechain_ps.get_referral_employee_user_id(
                current_user.sysuser.id, position.id)

            if recommender_user_id:
                recom_employee = yield self.employee_ds.get_employee(conds={
                    "sysuser_id": current_user.sysuser.id,
                    "status":     const.NO,
                    "disable":    const.NO,
                    "activation": const.NO,
                })
                recommender_wxuser_id = recom_employee.wxuser_id or 0

        sharechain_ps = None
        self.logger.debug("[get_recommend_user]end")
        return recommender_user_id, recommender_wxuser_id, recom_employee

    @gen.coroutine
    def opt_add_reward(self, apply_id, current_user, position, is_platform):
        """ 添加积分
        :param apply_id:
        :param current_user:
        :param position:
        :param is_platform:
        """
        self.logger.debug("[opt_add_reward]start")
        recommender_user_id, recommender_wxuser_id, recom_employee = yield self.get_recommend_user(
            current_user, position, is_platform)

        self.logger.debug(
            "[opt_add_reward]recommender_user_id:{}, recommender_wxuser_id:{}, recom_employee:{}".format(
                recommender_user_id, recommender_wxuser_id, recom_employee))
        points_conf = yield self.hr_points_conf_ds.get_points_conf(conds={
            "company_id":  position.company_id,
            "template_id": self.constant.RECRUIT_STATUS_APPLY_ID,
        }, appends=["ORDER BY id DESC", "LIMIT 1"])

        if recom_employee and points_conf:
            self.logger.debug("[opt_add_reward]添加积分")
            yield self.user_employee_points_record_ds.create_user_employee_points_record(
                fields={
                    "employee_id":    recom_employee.id,
                    "application_id": apply_id,
                    "recom_wxuser":   recommender_wxuser_id,
                    "reason":         points_conf.status_name,
                    "award":          points_conf.reward,
                    "recom_user_id":  recommender_user_id,
                })

            # 更新员工的积分
            employee_sum = yield self.user_employee_points_record_ds.get_user_employee_points_record_sum(
                conds={
                    "employee_id": recom_employee.id
                }, fields=["award"])

            if employee_sum.sum_award:
                yield self.user_employee_ds.update_employee(conds={
                    "id":         recom_employee.id,
                    "company_id": recom_employee.company_id,
                }, fields={
                    "award": int(employee_sum.sum_award),
                })

                #     @gen.coroutine
                #     def opt_send_redpacket(self, current_user, position):
                #         """
                #         发送申请红包
                #         :param current_user:
                #         :param position:
                #         :return:
                #         """
                #         # TODO 待yiliang校验
                #         yield self.redpacket_ps.handle_red_packet_position_related(
                #             current_user,
                #             position,
                #             redislocker=self.redis,
                #             is_apply=True
                #         )
                #
        self.logger.debug("[opt_add_reward]end")

    @gen.coroutine
    def opt_send_applier_msg(self, apply_id, current_user, position, is_platform=True):
        """
        向求职者发送消息通知（消息模板，短信）
        :param apply_id:
        :param current_user:
        :param position:
        :return:
        """

        self.logger.debug("[opt_send_applier_msg]start")
        # 发送消息模板，先发企业号，再发仟寻
        link = make_url(
            path.USERCENTER_APPLYRECORD.format(apply_id),
            host=self.settings.platform_host,
            wechat_signature=current_user.wechat.signature)

        self.logger.debug("[opt_send_applier_msg]link:{}".format(link))

        res_bool = False
        if current_user.wxuser:
            res_bool = yield application_notice_to_applier_tpl(current_user.wechat.id,
                                                          current_user.wxuser.openid,
                                                          link,
                                                          position.title,
                                                          current_user.company.name)
        if not res_bool:
            params = ObjectDict({
                "company": current_user.company.abbreviation or current_user.company.name,
                "position": position.title
            })

            yield self.thrift_mq_ds.send_sms(SmsType.NEW_APPLIACATION_TO_APPLIER_SMS, current_user.sysuser.mobile,
                                             params, isqx=not is_platform)

        self.logger.debug("[opt_send_applier_msg]end")


    @gen.coroutine
    def opt_send_recommender_msg(self, recommend_user_id, current_user,
                                 position, profile):
        """
        向推荐人发送消息模板
        :param recommend_user_id:
        :param current_user:
        :param position:
        :param profile:
        :return:
        """
        self.logger.debug("[opt_send_recommender_msg]start")

        recom_record = yield self.candidate_recom_record_ds.get_candidate_recom_record(
            conds={
                "position_id":       position.id,
                "presentee_user_id": current_user.sysuser.id,
                "post_user_id":      recommend_user_id,
            }, appends=["LIMIT 1"])

        if recom_record and current_user.recom.id:
            profile_ps = ProfilePageService()
            work_exp_years = profile_ps.calculate_workyears(
                profile.get("workexps", []))
            job = profile_ps.get_job_for_application(profile)
            recent_job = job.get("company_name", "")

            link = make_url(path.EMPLOYEE_RECOMMENDS,
                            host=self.settings.platform_host,
                            wechat_signature=current_user.wechat.signature)

            self.logger.debug("[opt_send_recommender_msg]link:{}".format(link))

            application_notice_to_recommender_tpl(current_user.wechat.id,
                                                  current_user.recom.openid,
                                                  link,
                                                  current_user.sysuser.name or current_user.sysuser.nickname,
                                                  position.title,
                                                  work_exp_years,
                                                  recent_job)
            profile_ps = None
        self.logger.debug("[opt_send_recommender_msg]end")

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
                    "position_id":       position.id,
                    "post_user_id":      recommend_user_id,
                    "presentee_user_id": current_user.sysuser.id,
                }, fields={
                    "app_id": apply_id
                }
            )
        self.logger.debug("[opt_update_candidate_recom_records]end")

    @gen.coroutine
    def opt_hr_msg(self, apply_id, current_user, profile, position, is_platform=True):

        self.logger.debug("[opt_hr_msg]start")
        # 1. 向 HR 发送消息模板通知，短信
        if position.publisher:
            profile_ps = ProfilePageService()
            work_exp_years = profile_ps.calculate_workyears(
                profile.get("workexps", []))
            job = profile_ps.get_job_for_application(profile)
            recent_job = job.get("company_name", "")

            hr_info = yield self.user_hr_account_ds.get_hr_account(conds={
                "id": position.publisher
            })
            is_ok = False
            self.logger.debug("[opt_hr_msg]hr_info:{}".format(hr_info))
            if hr_info.wxuser_id:
                hr_wxuser = yield self.user_wx_user_ds.get_wxuser(conds={
                    "id":        hr_info.wxuser_id,
                    "wechat_id": self.settings.helper_wechat_id,
                })
                if hr_wxuser.openid:
                    is_ok = application_notice_to_hr_tpl(
                        self.settings.helper_wechat_id,
                        hr_wxuser.openid,
                        hr_info.name or hr_wxuser.nickname,
                        position.title,
                        current_user.sysuser.name or current_user.sysuser.nickname,
                        work_exp_years,
                        recent_job)

            if not is_ok:
                # 消息模板发送失败时，只对普通客户发送短信
                if hr_info.mobile and hr_info.account_type == 2:
                    params = ObjectDict({
                        "position": position.title
                    })
                    yield self.thrift_mq_ds.send_sms(SmsType.NEW_APPLICATION_TO_HR_SMS,
                                                     current_user.sysuser.mobile,
                                                     params, isqx=not is_platform)
            profile_ps = None

        # 2. 向 HR 发送邮件通知
        yield self.opt_send_hr_email(apply_id, current_user, profile, position, hr_info)
        self.logger.debug("[opt_hr_msg]end")

    @gen.coroutine
    def opt_send_hr_email(self, apply_id, current_user, profile, position, hr_info):

        self.logger.debug("[opt_send_hr_email]start")

        html_fname = "{aid}.html".format(aid=apply_id)
        pdf_fname = "{aid}.pdf".format(aid=apply_id)

        cmd = get_create_pdf_by_html_cmd(html_fname, pdf_fname)

        # 生成pdf文件名发生改变,现在的生成方式是按照一个appid生成
        resume_tpath = os.path.join(self.settings.template_path, 'weixin/application/')

        # template_others = custom_kvmapping(others_json)
        template_others = ObjectDict()

        self.logger.debug("[send_mail_hr]html_fname:{}".format(html_fname))
        self.logger.debug("[send_mail_hr]pdf_fname:{}".format(pdf_fname))
        self.logger.debug("[send_mail_hr]cmd:{}".format(cmd))
        self.logger.debug("[send_mail_hr]resume_tpath:{}".format(resume_tpath))
        self.logger.debug("[send_mail_hr]profile:{}".format(profile))
        self.logger.debug("[send_mail_hr]template_others:{}".format(template_others))
        self.logger.debug("[send_mail_hr]resume_path:{}".format(self.settings.resume_path))

        save_application_file(
            resume_tpath,
            'resume2pdf_new.html',
            profile,
            html_fname,
            template_others,
            self.settings.resume_path)

        def send(data):
            self.logger.info("[opt_send_hr_email][send]Finish creating pdf resume : {}".format(pdf_fname))
            self.logger.info("[opt_send_hr_email][send]response data: " + str(data))

        def send_mail_hr():

            send_email = position.hr_email or hr_info.email
            employee = current_user.employee
            employee_cert_conf = yield self.hr_employee_cert_conf_ds.get_employee_cert_conf(
                current_user.company.id)
            conf = employee_cert_conf.custom or "自定义字段"

            self.logger.debug("[send_mail_hr]send_email:{}".format(send_email))
            self.logger.debug("[send_mail_hr]employee:{}".format(employee))
            self.logger.debug("[send_mail_hr]employee_cert_conf:{}".format(employee_cert_conf))
            self.logger.debug("[send_mail_hr]conf:{}".format(conf))

            if position.email_notice == const.OLD_YES and send_email:
                send_mail_notice_hr(
                    position, employee, conf,
                    current_user.sysuser.id, profile, send_email,
                    template_others, pdf_fname)

                self.logger.debug("[send_mail_hr]position:{}".format(position))
                self.logger.debug("[send_mail_hr]employee:{}".format(employee))
                self.logger.debug("[send_mail_hr]conf:{}".format(conf))
                self.logger.debug("[send_mail_hr]current_user.sysuser.id:{}".format(current_user.sysuser.id))
                self.logger.debug("[send_mail_hr]profile:{}".format(profile))
                self.logger.debug("[send_mail_hr]send_email:{}".format(send_email))
                self.logger.debug("[send_mail_hr]template_others:{}".format(template_others))
                self.logger.debug("[send_mail_hr]pdf_fname:{}".format(pdf_fname))

                self.logger.info(
                    "[opt_send_hr_email]Send application to HR success:sysuser id:{sid},"
                    "aid:{aid},pid:{pid},email:{email}"
                        .format(sid=current_user.sysuser.id,
                                aid=apply_id,
                                pid=position.id,
                                email=send_email))
            else:
                self.logger.info("[opt_send_hr_email]not send email。"
                                 "email_notice:{}, email:{}".format(position.email_notice, send_email))

        self.logger.debug("[send_mail_hr]html_fname:{}".format(html_fname))
        self.logger.debug("[send_mail_hr]pdf_fname:{}".format(pdf_fname))

        self.logger.debug("[send_mail_hr]cmd:{}".format(cmd))
        self.logger.debug("[send_mail_hr]resume_path:{}".format(self.settings.resume_path))

        Sub().subprocess(cmd, self.settings.resume_path, send, send_mail_hr)
        self.logger.debug("[opt_send_hr_email]end")

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
                company_abbr =company_abbr,
                header_company_abbr = trunc(company_abbr, const.MANDRILL_EMAIL_HEADER_LIMIT),
                applier_name = applier_name,
                header_applier_name = trunc(applier_name, const.MANDRILL_EMAIL_HEADER_LIMIT),
                invitation_code = invitation_code
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

#
# import unittest
#
# class ApplicationPSTest(unittest.TestCase):
#     def setUp(self):
#         super().setUp()
#         self.json_config = [{'fields': [{'company_id':        0,
#                                          'create_time':       '2015-11-09 23:11:59',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'name',
#                                          'field_title':       '姓名',
#                                          'field_type':        0,
#                                          'field_value':       [['']],
#                                          'id':                2,
#                                          'is_basic':          0,
#                                          'map':               'basicinfo.name',
#                                          'priority':          2,
#                                          'required':          0,
#                                          'update_time':       '2015-12-04 08:24:39'},
#                                         {'company_id':        0,
#                                          'create_time':       '2015-11-09 23:11:59',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'gender',
#                                          'field_title':       '性别',
#                                          'field_type':        3,
#                                          'field_value':       [
#                                              ['男', '1'], ['女', '2']],
#                                          'id':                5,
#                                          'is_basic':          0,
#                                          'map':               'basicinfo.gender',
#                                          'priority':          5,
#                                          'required':          0,
#                                          'update_time':       '2015-12-03 12:48:36'},
#                                         {'company_id':        0,
#                                          'create_time':       '2015-11-09 23:12:00',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'idnumber',
#                                          'field_title':       '身份证号码',
#                                          'field_type':        0,
#                                          'field_value':       [['']],
#                                          'id':                15,
#                                          'is_basic':          0,
#                                          'map':               'basicinfo.idnumber',
#                                          'priority':          15,
#                                          'required':          0,
#                                          'update_time':       '2015-11-27 06:33:32'},
#                                         {'company_id':        0,
#                                          'create_time':       '2015-11-09 23:11:59',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'mobile',
#                                          'field_title':       '手机',
#                                          'field_type':        0,
#                                          'field_value':       [['']],
#                                          'id':                3,
#                                          'is_basic':          0,
#                                          'map':               'basicinfo.mobile',
#                                          'priority':          3,
#                                          'required':          0,
#                                          'update_time':       '2015-12-04 08:24:39'},
#                                         {'company_id':        0,
#                                          'create_time':       '2015-11-09 23:11:59',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'email',
#                                          'field_title':       '邮箱',
#                                          'field_type':        0,
#                                          'field_value':       [['']],
#                                          'id':                11,
#                                          'is_basic':          0,
#                                          'map':               'basicinfo.email',
#                                          'priority':          11,
#                                          'required':          0,
#                                          'update_time':       '2015-11-27 06:33:32'},
#                                         {'company_id':        0,
#                                          'create_time':       '2015-11-09 23:12:00',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'location',
#                                          'field_title':       '现居住地',
#                                          'field_type':        0,
#                                          'field_value':       [['']],
#                                          'id':                16,
#                                          'is_basic':          0,
#                                          'map':               'basicinfo.location',
#                                          'priority':          16,
#                                          'required':          0,
#                                          'update_time':       '2015-11-27 06:33:32'},
#                                         {'company_id':        0,
#                                          'create_time':       '2016-04-18 16:06:42',
#                                          'disable':           0,
#                                          'field_description': '',
#                                          'field_name':        'Address',
#                                          'field_title':       '通讯地址',
#                                          'field_type':        0,
#                                          'field_value':       [['']],
#                                          'id':                61,
#                                          'is_basic':          0,
#                                          'map':               '',
#                                          'priority':          61,
#                                          'required':          0,
#                                          'update_time':       '2016-11-24 10:03:01'}],
#                              'title':  '基本信息'},
#                             {'fields':      [{'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'degree',
#                                               'field_title':       '学历',
#                                               'field_type':        10,
#                                               'field_value':       [
#                                                   ['大专以下', '1'],
#                                                   ['大专', '2'],
#                                                   ['本科', '3'],
#                                                   ['硕士', '4'],
#                                                   ['博士', '5'],
#                                                   ['博士以上', '6']],
#                                               'id':                17,
#                                               'is_basic':          0,
#                                               'map':               'basicinfo.degree',
#                                               'priority':          17,
#                                               'required':          0,
#                                               'update_time':       '2016-04-27 13:56:18'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'graduation',
#                                               'field_title':       '预计毕业时间',
#                                               'field_type':        6,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                19,
#                                               'is_basic':          1,
#                                               'map':               'score.graduation',
#                                               'priority':          19,
#                                               'required':          0,
#                                               'update_time':       '2015-11-27 06:33:32'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'education',
#                                               'field_title':       '教育经历',
#                                               'field_type':        9,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                18,
#                                               'is_basic':          0,
#                                               'map':               'education',
#                                               'priority':          18,
#                                               'required':          0,
#                                               'update_time':       '2015-11-27 06:33:32'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'gpa',
#                                               'field_title':       'GPA',
#                                               'field_type':        11,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                28,
#                                               'is_basic':          1,
#                                               'map':               'score.gpa',
#                                               'priority':          28,
#                                               'required':          0,
#                                               'update_time':       '2015-12-04 07:28:39'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'cet4',
#                                               'field_title':       '四级成绩',
#                                               'field_type':        11,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                22,
#                                               'is_basic':          1,
#                                               'map':               'score.cet4',
#                                               'priority':          22,
#                                               'required':          0,
#                                               'update_time':       '2015-12-04 07:28:39'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'cet6',
#                                               'field_title':       '六级成绩',
#                                               'field_type':        11,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                23,
#                                               'is_basic':          1,
#                                               'map':               'score.cet6',
#                                               'priority':          23,
#                                               'required':          0,
#                                               'update_time':       '2015-12-04 07:28:39'}],
#                              'placeholder': '第2步',
#                              'title':       '第2步'},
#                             {'fields':      [{'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:01',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'internship',
#                                               'field_title':       '实习经历',
#                                               'field_type':        9,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                35,
#                                               'is_basic':          1,
#                                               'map':               'workexperience.internship',
#                                               'priority':          34,
#                                               'required':          0,
#                                               'update_time':       '2015-11-30 05:29:10'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'schooljob',
#                                               'field_title':       '校内职务',
#                                               'field_type':        9,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                31,
#                                               'is_basic':          1,
#                                               'map':               'score.schooljob',
#                                               'priority':          31,
#                                               'required':          0,
#                                               'update_time':       '2015-11-27 06:33:33'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:00',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'competition',
#                                               'field_title':       '获得奖项',
#                                               'field_type':        4,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                29,
#                                               'is_basic':          1,
#                                               'map':               'score.competition',
#                                               'priority':          29,
#                                               'required':          0,
#                                               'update_time':       '2016-04-25 10:58:54'}],
#                              'placeholder': '第3步',
#                              'title':       '第3步'},
#                             {'fields':      [{'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:01',
#                                               'disable':           0,
#                                               'field_description': '输入您对自己的简短评价。请简明扼要的说明您最大的优势是什么',
#                                               'field_name':        'remarks',
#                                               'field_title':       '自我介绍',
#                                               'field_type':        1,
#                                               'field_value':       [
#                                                   ['']],
#                                               'id':                45,
#                                               'is_basic':          0,
#                                               'map':               'remarks',
#                                               'priority':          45,
#                                               'required':          0,
#                                               'update_time':       '2015-11-27 06:33:34'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:01',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'expectsalary',
#                                               'field_title':       '期望年薪',
#                                               'field_type':        10,
#                                               'field_value':       [
#                                                   ['6万以下', '1'],
#                                                   ['6万-8万', '2'],
#                                                   ['8万-12万', '3'],
#                                                   ['12-20万', '4'],
#                                                   ['20万-30万', '5'],
#                                                   ['30万以上', '6']],
#                                               'id':                39,
#                                               'is_basic':          0,
#                                               'map':               'intention.expectsalary',
#                                               'priority':          39,
#                                               'required':          0,
#                                               'update_time':       '2016-04-28 20:56:20'},
#                                              {'company_id':        0,
#                                               'create_time':       '2015-11-09 23:12:01',
#                                               'disable':           0,
#                                               'field_description': '',
#                                               'field_name':        'trip',
#                                               'field_title':       '是否接受长期出差',
#                                               'field_type':        3,
#                                               'field_value':       [
#                                                   ['接受', '1'],
#                                                   ['不接受', '2']],
#                                               'id':                43,
#                                               'is_basic':          0,
#                                               'map':               'intention.trip',
#                                               'priority':          43,
#                                               'required':          1,
#                                               'update_time':       '2016-05-03 11:44:29'}],
#                              'placeholder': '第4步',
#                              'title':       '第4步'}]
#
#         self.field_value = '[{"fields":[{"field_description":"","company_id":0,"create_time":"2015-11-09 23:11:59","priority":2,"field_title":"姓名","required":0,"is_basic":0,"field_name":"name","update_time":"2015-12-04 08:24:39","disable":0,"field_value":[[""]],"id":2,"field_type":0,"map":"basicinfo.name"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:11:59","priority":3,"field_title":"手机","required":0,"is_basic":0,"field_name":"mobile","update_time":"2015-12-04 08:24:39","disable":0,"field_value":[[""]],"id":3,"field_type":0,"map":"basicinfo.mobile"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:12:00","priority":18,"field_title":"教育经历","required":0,"is_basic":0,"field_name":"education","update_time":"2015-11-27 06:33:32","disable":0,"field_value":[[""]],"id":18,"field_type":9,"map":"education"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:12:00","priority":33,"field_title":"工作经历","required":0,"is_basic":0,"field_name":"workexp","update_time":"2015-11-27 06:33:33","disable":0,"field_value":[[""]],"id":33,"field_type":9,"map":"workexp"},{"field_description":"","company_id":0,"create_time":"2015-11-09 23:12:00","priority":34,"field_title":"项目经历","required":0,"is_basic":0,"field_name":"projectexp","update_time":"2015-11-27 06:33:34","disable":0,"field_value":[[""]],"id":34,"field_type":9,"map":"projectexp"}],"title":"基本信息"}]'
#
#     def test_make_fields_to_check(self):
#         def _merge(x, y):
#             x.extend(y)
#             return x
#
#         json_config = objectdictify(self.json_config)
#         fields = functools.reduce(_merge, [page.fields for page in json_config])
#         fileds_to_check = [f for f in objectdictify(fields) if f.required == const.OLD_YES]
#         field_names = [f.field_name for f in fileds_to_check]
#         self.assertIn('gpa', field_names)
#         self.assertIn('idnumber', field_names)
#         self.assertIn('Address', field_names)
#
#     def test_filed_value(self):
#         pprint.pprint(json_decode(self.field_value))
#
#
# if __name__ == "__main__":
#     unittest.main()
