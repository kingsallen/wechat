# coding=utf-8

import json
import functools
import uuid
import re
import traceback

from tornado import gen
from tornado.escape import json_decode, json_encode
from tornado.concurrent import run_on_executor

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
from util.tool.dict_tool import objectdictify, purify
from util.tool.pdf_tool import save_application_file, get_create_pdf_by_html_cmd
from util.tool.mail_tool import send_mail_notice_hr
from util.wechat.template import application_notice_to_applier_tpl, application_notice_to_recommender_tpl, application_notice_to_hr_tpl
from thrift_gen.gen.mq.struct.ttypes import SmsType
import tornado.concurrent

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
    def get_custom_tpl_all(self):
        ret = yield self.config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
            conds={'disable': const.OLD_YES},
            fields=['field_name', 'field_title', 'map']
        )
        return ret

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
        :param profile: 全 profile
        :param app_id:  申请id
        :param position: 申请职位
        :return: (result, message)
        """
        if not position.app_cv_config_id:
            return True, None

        resume_other = ObjectDict()

        cv_conf = yield self.get_hr_app_cv_conf(position.app_cv_config_id)
        fields = self.make_fields_list(cv_conf)

        if profile.others:
            p_other = json.loads(profile.others[0].get('other'))

            for field in fields:
                if p_other.get(field):
                    resume_other.update({field: p_other.get(field)})
            resume_other_to_insert = json_dumps(resume_other)
            self.logger.debug('resume_other_to_insert: %s' % resume_other_to_insert)
            yield self.hr_resume_other_ds.insert_job_resume_other({
                'appid': app_id,
                'other': resume_other_to_insert
            })
            return True, None
        else:
            raise ValueError('profile has no other field')

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
        yield self.opt_send_recommender_msg(recommender_user_id, current_user, position)
        #4. 更新挖掘被动求职者信息
        yield self.opt_update_candidate_recom_records(apply_id, current_user, recommender_user_id, position)
        #5. 向 HR 发送消息通知（消息模板，短信，邮件）
        yield self.opt_hr_msg(current_user, position, is_platform)

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
                                 position):
        """
        向推荐人发送消息模板
        :param recommend_user_id:
        :param current_user:
        :param position:
        :param profile:
        :return:
        """
        self.logger.debug("[opt_send_recommender_msg]start")
        profile = current_user.profile
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
    def opt_hr_msg(self, current_user, position, is_platform=True):

        self.logger.debug("[opt_hr_msg]start")
        # 1. 向 HR 发送消息模板通知，短信
        profile = current_user.profile
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

    @gen.coroutine
    def opt_send_hr_email(self, apply_id, current_user, position):

        profile_ps = ProfilePageService()
        self.logger.debug("[opt_send_hr_email]start")

        html_fname = "{aid}.html".format(aid=apply_id)
        pdf_fname = "{aid}.pdf".format(aid=apply_id)

        hr_info = yield self.user_hr_account_ds.get_hr_account(conds={
            "id": position.publisher
        })
        profile = current_user.profile
        cmd = get_create_pdf_by_html_cmd(html_fname, pdf_fname)

        other_json = json.loads(profile.get("others", [])[0].get("other")) if profile.get("others", []) else ObjectDict()
        template_others = yield self.custom_kvmapping(other_json)

        self.logger.debug("[send_mail_hr]html_fname:{}".format(html_fname))
        self.logger.debug("[send_mail_hr]pdf_fname:{}".format(pdf_fname))
        self.logger.debug("[send_mail_hr]cmd:{}".format(cmd))
        self.logger.debug("[send_mail_hr]profile:{}".format(profile))
        self.logger.debug("[send_mail_hr]template_others:{}".format(template_others))
        self.logger.debug("[send_mail_hr]resume_path:{}".format(self.settings.resume_path))

        # 常量字段
        res_degree = yield self.infra_dict_ds.get_const_dict(parent_code=const.CONSTANT_PARENT_CODE.DEGREE_USER)
        res_language = yield self.infra_dict_ds.get_const_dict(parent_code=const.CONSTANT_PARENT_CODE.LANGUAGE_FRUENCY)
        dict_conf = ObjectDict(
            degree=res_degree,
            language=res_language,
            email_basicinfo=profile_ps.EMAIL_BASICINFO.keys(),
            profile_basicinfo=profile_ps.EMAIL_BASICINFO,
            intention=profile_ps.EMAIL_INTENTION.keys(),
            profile_intention=profile_ps.EMAIL_INTENTION,
        )

        work_exp_years = profile_ps.calculate_workyears(
            profile.get("workexps", []))

        save_application_file(
            profile,
            html_fname,
            template_others,
            self.settings.resume_path,
            dict_conf,
        )

        def send(data):
            self.logger.info("[opt_send_hr_email][send]Finish creating pdf resume : {}".format(pdf_fname))
            self.logger.info("[opt_send_hr_email][send]response data: " + str(data))

        def send_mail_hr():
            self.logger.debug("send_mail_hr start start start!!!")

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
                    position, employee, conf, profile, send_email,
                    template_others, dict_conf, work_exp_years, pdf_fname)

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

        profile_ps = None

        self.logger.debug("[send_mail_hr]html_fname:{}".format(html_fname))
        self.logger.debug("[send_mail_hr]pdf_fname:{}".format(pdf_fname))

        self.logger.debug("[send_mail_hr]cmd:{}".format(cmd))
        self.logger.debug("[send_mail_hr]resume_path:{}".format(self.settings.resume_path))

        try:
            # Sub().subprocess(cmd, self.settings.resume_path, send, send_mail_hr)
            import subprocess
            completed_process = subprocess.run(cmd, check=True, shell=True,
                                               stdout=subprocess.PIPE)
            if completed_process.returncode == 0:
                self.logger.debug(completed_process.stdout)
                send_mail_hr()
            else:
                self.logger.error('generate pdf error:%s' % completed_process.stderr)

            self.logger.debug("[opt_send_hr_email]end")
        except Exception as e:
            self.logger.error(traceback.format_exc())

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

    @gen.coroutine
    def custom_fields_need_kvmapping(self, config_cv_tpls):
        """
        工具方法，
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
            value_list = re.split(',|:', record.field_value)
            value = {}
            index = 0
            while True:
                try:
                    if value_list[index] and value_list[index + 1]:
                        value.update(
                            {value_list[index + 1]: value_list[index]})
                        index += 2
                except Exception:
                    break
            value.update({'0': ''})

            kvmappinp_ret.update({
                record.field_name: {
                    "title": record.field_title,
                    "value": value}
            })
            return kvmappinp_ret

    @gen.coroutine
    def custom_kvmapping(self, others_json):
        """
        把 profile others 字段中的 key 转换为 value, 供模板使用
        :param others_json
        :return:
        others:{
            "iter_others":[["学历", "本科"], ["城市", "佛山"]....],
            "special_others":{
                "projectexp":[
                    "start": "2015-06"
                    ...
                ],
                "awards":[
                    ...
                ]
            }
        }
        """
        # 自定义字段中的符复合字段
        CV_OTHER_SPECIAL_KEYS = [
            "recentjob", "schooljob", "education", "reward", "language",
            "competition", "workexp", "projectexp", "internship", "industry",
            "position", "IDPhoto"]

        # 这些字段虽然是复合字段，但是需要在发给 hr 的邮件中被当成普通字段看待
        CV_OTHER_SPECIAL_ITER_KEYS = [
            "reward", "language", "competition", "industry", "position"]

        config_cv_tpls = yield self.config_sys_cv_tpl_ds.get_config_sys_cv_tpls(
            conds={'disable': const.OLD_YES},
            fields=['field_name', 'field_title', 'map', 'field_value']
        )

        # 先找出那哪些自定义字段需要做 kvmapping
        kvmap = yield self.custom_fields_need_kvmapping(config_cv_tpls)

        others = ObjectDict()
        iter_others = []
        special_others = {}

        for key, value in purify(others_json).items():
            if key == "picUrl":
                # because we already have IDPhoto as key
                continue
            if key in CV_OTHER_SPECIAL_KEYS:
                special_others[key] = value
            else:
                iter_other = []
                iter_other.append(kvmap.get(key, {}).get("title", ""))
                if kvmap.get(key, {}).get("value"):
                    iter_other.append(
                        kvmap[key].get("value").get(str(value), ""))
                else:
                    iter_other.append(value)
                iter_others.append(iter_other)

            display_name_mapping = {
                e.get('field_name'): e.get('field_title')
                for e in config_cv_tpls
                }

            # 将部分 special_keys 转为iter_others
            if key in CV_OTHER_SPECIAL_ITER_KEYS:
                iter_other = []
                if isinstance(value, list) and len(value) > 0:
                    iter_other.append(display_name_mapping.get(key))
                    msg = " ".join(value)
                    iter_other.append(msg)
                if key == "industry" and value:
                    # 期望工作行业，存储为字典值，需要处理为具体的行业名称
                    iter_other.append(display_name_mapping.get(key))
                    iter_other.append(kvmap.get(key).get('value').get(value))
                elif key == "position" and value:
                    # 期望职能
                    iter_other.append(display_name_mapping.get(key))
                    iter_other.append(value)
                iter_others.append(iter_other)

        others.iter_others = iter_others
        others.special_others = special_others
        return others

#
# if __name__ == '__main__':
#     import subprocess
#     result = subprocess.run(['ls', '-l'])
#     print(result.stdout)
#
#     print(result.stderr)
