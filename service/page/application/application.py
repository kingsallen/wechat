# coding=utf-8

import uuid
import json

from tornado import gen

import conf.message as msg
import conf.path as path
import conf.common as const
from service.page.user.sharechain import SharechainPageService
from service.page.base import PageService
from cache.application.email_apply import EmailApplyCache
from util.common import ObjectDict
from util.tool.url_tool import make_url
from util.wechat.template import application_notice_to_applier_tpl, application_notice_to_recommender_tpl, application_notice_to_hr_tpl

class ApplicationPageService(PageService):
    pass

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
            "applier_id": user_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_position_applied_cnt(self, conds, fields):
        """返回申请数统计"""

        response = yield self.job_application_ds.get_position_applied_cnt(conds=conds, fields=fields)

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
            'user_id': user_id,
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

#     @gen.coroutine
#     def custom_check_failure_redirection(self, profile, position, user):
#         """
#         处理自定义简历校验和失败后的跳转
#         hanlder 调用完此方法后需要立即 return
#         """
#
#         cv_conf = yield self.hr_app_cv_conf_ds.get_app_cv_conf(conds={
#             "id": position.app_cv_config_id,
#             "disable": const.NO,
#         })
#
#         json_config = json.loads(cv_conf.field_value)
#
#         self.logger.debug("json_confg:{}".format(json_config))
#
#         for c in json_config:
#             fields = c.get("fields")
#             for field in fields:
#                 field_name = field.get("field_name")
#                 required = not field.get("required")
#                 # 校验失败条件:
#                 # 1. rquired and
#                 # 2. field_name 在 profile 对应字端中,但是 profile 中这个字段为空值
#                 #    or
#                 #    field_name 是纯自定义字段,但是在 custom_others 中没有这个值
#                 check_ret = yield self.check_custom_field(profile, field_name, user)
#                 if required and not check_ret:
#                     self.logger.debug("自定义字段必填校验错误, 返回app_cv_conf.html\n"
#                                       "field_name:{}".format(field_name))
#                     # TODO
#                     resume_dict = _generate_resume_cv(profile)
#                     self.logger.debug("resume_dict: {}".format(resume_dict))
#
#                     raise gen.Return((True, resume_dict, json_config))
#
#         raise gen.Return((False, None, None))
#
#     @gen.coroutine
#     def check_custom_field(self, profile, field_name, user):
#         """
#         检查自定义字段必填项
#         """
#
#         profile_id = profile.get("profile", {}).get("id", None)
#         assert profile_id is not None
#
#         # TODO
#         if field_name in cv_profile_keys():
#             self.logger.debug("field_name: {}".format(field_name))
#
#             mapping = const.CUSTOM_FIELD_NAME_TO_PROFILE_FIELD[field_name]
#             if mapping.startswith("user_user"):
#
#                 sysuser_id = profile.get("profile", {}).get("user_id", None)
#                 if not sysuser_id:
#                     return False
#                 column_name = mapping.split(".")[1]
#                 self.logger.debug("sysuser_id:{}, column_name:{}".format(sysuser_id, column_name))
#                 if column_name not in ['email', 'name', 'mobile', 'headimg']:
#                     return False
#                 self.logger.debug("sysuser:{}".format(user))
#                 return bool(user.__getattr__(column_name))
#
#             if mapping.startswith("profile_education"):
#                 return bool(profile.get('educations', []))
#
#             if mapping.startswith("profile_workexp"):
#                 return bool(profile.get('workexps', []))
#
#             if mapping.startswith("profile_projectexp"):
#                 return bool(profile.get('projectexps', []))
#
#             if mapping.startswith("profile_basic"):
#                 table_name, column_name = self.__split_dot(mapping)
#                 key_1 = table_name.split("_")[1]  # should be "basic"
#                 key_2 = column_name
#                 return bool(profile.get(key_1, {}).get(key_2, None))
#
#         # TODO
#         elif field_name in cv_pure_custom_keys():
#             other = get_profile_other_by_profile_id(handler.db, profile_id)
#
#             # 如果存在 other row ,获取 other column
#             if other:
#                 other = other.other
#             else:
#                 return False
#
#             self.logger.debug("other: {}".format(other))
#             other_json = json.loads(other)
#             self.logger.debug("other_json: {}".format(other_json))
#
#             if not other_json or "null" in other_json:
#                 return False
#             else:
#                 return bool(other_json.get(field_name))
#         else:
#             self.logger.error(
#                 "{} is in neither _cv_profile_keys nor _cv_pure_custom_keys..."
#                     .format(field_name)
#             )
#             return False
#
    @gen.coroutine
    def create_email_apply(self, params, position, current_user, is_platform=True):
        """
        创建Email申请
        :param params:
        :param position:
        :param current_user:
        :param is_platform:
        :return:
        """

        check_status, message = self.check_position(position, current_user)
        self.logger.debug("[create_email_reply]check_status:{}, message:{}".format(check_status, message))
        if not check_status:
            raise gen.Return((False, message))

        # 获取推荐人信息
        recommender_user_id, recommender_wxuser_id, recom_employee = yield self.get_recommend_user(current_user, position, is_platform)

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
            email_status=1  # email解析状态: 0，有效；1,未收到回复邮件；2，文件格式不支持；3，附件超过10M；9，提取邮件失败
        )

        self.logger.debug(
            "[create_email_reply]params_for_application:{}".format(recommender_wxuser_id))

        ret = yield self.infra_application_ds.create_application(params_for_application)

        # 申请创建失败,  跳转到申请失败页面
        if not ret.status != const.API_SUCCESS:
            message=msg.CREATE_APPLICATION_FAILED
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
        rst = send_email_create_application_notice(email_params, position)  # 1是platform, 2是qx
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
            email_address = params.email,
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

        self.email_apply_session.save_email_apply_sessions(uuidcode, value_dict)
        self.logger.debug("[create_email_profile]value_dict:{}".format(value_dict))
        # 求职者发送Email创建邮件
        rst = send_email_create_profile_notice(email_params)
        self.logger.debug("[create_email_profile]Send Email to creator " + str(rst))

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
    def create_application(self, params, position, current_user, is_platform=True):

        # 1.初始化
        check_status, message = yield self.check_position(position, current_user)
        self.logger.debug("[create_reply]check_status:{}, message:{}".format(check_status, message))
        if not check_status:
            return False, message, None

        # # 2.校验
        # has_profile, profile = yield self.profile_ps.has_profile(current_user.sysuser.id)
        # if not has_profile:
        #     # TODO message 可调整
        #     raise gen.Return((False, None, None))

        # # 如果有 profile 但是是自定义职位, 检查该 profile 是否符合自定义简历必填项
        # if position.app_cv_config_id:
        #     is_true, resume_dict, json_config = yield self.custom_check_failure_redirection(
        #         profile, position, current_user.sysuser)
        #     if is_true:
        #         # TODO message 可调整
        #         raise gen.Return((False, None, None))

        # 3.创建申请
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
        else:
            pass

        apply_id = ret.data.jobApplicationId

        # # 4. 将本次提交的自定义字段存到 job_resume_other 中去
        # yield self._create_job_resume_other(position, params.cv)

        # 申请的后续处理
        self.logger.debug("[post_apply]投递后续处理")

        #1. 添加积分
        yield self.opt_add_reward(apply_id, current_user, position, is_platform)

        #2. 向求职者发送消息通知（消息模板，短信）
        # yield self.opt_send_applier_msg(apply_id, current_user, position)
        #3. 向推荐人发送消息模板
        # yield self.opt_send_recommender_msg(recommender_user_id, current_user, position, current_user.profile)
        #4. 更新挖掘被动求职者信息
        # yield self.opt_update_candidate_recom_records(apply_id, current_user, recommender_user_id, position)
        #5. 向 HR 发送消息通知（消息模板，短信，邮件）
        # yield self.opt_hr_msg(current_user, current_user.profile, position)

        # TODO (tangyiliang) 发红包
        # yield self.opt_send_redpacket(current_user, position)

        return True, msg.RESPONSE_SUCCESS, apply_id


    @gen.coroutine
    def get_recommend_user(self, current_user, position, is_platform):

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
                    "status": const.NO,
                    "disable": const.NO,
                    "activation": const.NO,
                })
                recommender_wxuser_id = recom_employee.wxuser_id or 0

        sharechain_ps = None
        return recommender_user_id, recommender_wxuser_id, recom_employee

#     @gen.coroutine
#     def _create_job_resume_other(self, position, cv):
#
#         others_json = {}
#         if position.app_cv_config_id > 0:
#             # 经过新六步过来的申请
#             if cv:
#                 if not isinstance(cv, dict):
#                     _cv = ujson.loads(cv)
#                 others_json = sub_dict(cv, cv_pure_custom_keys())
#                 insert_hr_resume_others(
#                     self.db, self.params.appid,
#                     ujson.dumps(others_json, ensure_ascii=False).encode("utf-8"))
#
#             # 已经有全字段
#             else:
#                 config = pos_ser.get_custom_template(position.app_cv_config_id)
#                 json_config = ujson.loads(config.field_value)
#
#                 profile_other = get_profile_other_by_profile_id(
#                     self.db, profile_id)
#                 if profile_other:
#                     profile_other = profile_other.other
#                     profile_other_dict = ujson.loads(profile_other)
#
#                     hr_resume_other = {}
#                     for c in json_config:
#                         fields = c.get("fields")
#                         for field in fields:
#                             field_name = field.get("field_name")
#                             if profile_other_dict.get(field_name):
#                                 hr_resume_other.update({
#                                     field_name: profile_other_dict.get(field_name)
#                                 })
#
#                     self.LOG.debug("hr_resume_other: {}".format(hr_resume_other))
#                     others_json = hr_resume_other
#                     insert_hr_resume_others(
#                         self.db, self.params.appid,
#                         ujson.dumps(hr_resume_other, ensure_ascii=False).encode(
#                             "utf-8"))
#
    @gen.coroutine
    def opt_add_reward(self, apply_id, current_user, position, is_platform):
        """ 添加积分
        :param apply_id:
        :param current_user:
        :param position:
        :param is_platform:
        """

        recommender_user_id, recommender_wxuser_id, recom_employee = yield self.get_recommend_user(current_user, position, is_platform)

        self.logger.debug("[opt_add_reward]recommender_user_id:{}, recommender_wxuser_id:{}, recom_employee:{}".format(recommender_user_id, recommender_wxuser_id,recom_employee))
        points_conf = yield self.hr_points_conf_ds.get_points_conf(conds={
            "company_id": position.company_id,
            "template_id": self.constant.RECRUIT_STATUS_APPLY_ID,
        }, appends=["ORDER BY id DESC", "LIMIT 1"])

        if recom_employee and points_conf:
            yield self.user_employee_points_record_ds.create_user_employee_points_record(fields={
                "employee_id": recom_employee.id,
                "application_id": apply_id,
                "recom_wxuser": recommender_wxuser_id,
                "reason": points_conf.status_name,
                "award": points_conf.reward,
                "recom_user_id": recommender_user_id,
            })

            # 更新员工的积分
            employee_sum = yield self.user_employee_points_record_ds.get_user_employee_points_record_sum(conds={
                "employee_id": recom_employee.id
            }, fields=["award"])

            if employee_sum.sum_award:
                yield self.user_employee_ds.update_employee(conds={
                    "id": recom_employee.id,
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
    @gen.coroutine
    def opt_send_applier_msg(self, apply_id, current_user, position):
        """
        向求职者发送消息通知（消息模板，短信）
        :param apply_id:
        :param current_user:
        :param position:
        :return:
        """

        # 发送消息模板，先发企业号，再发仟寻
        link = make_url(
            path.USERCENTER_APPLYRECORD.format(apply_id),
            host=self.settings.platform_host,
            wechat_signature=current_user.wechat.signature)

        self.logger.debug("[opt_send_applier_msg]link:{}".format(link))

        res = yield application_notice_to_applier_tpl(current_user.wechat.id,
                                                      current_user.wxuser.openid,
                                                      link,
                                                      position.title,
                                                      current_user.company.name)
        if not res:
            # TODO 发送短信
            # data = ObjectDict({
            #     "mobile": self.current_user.sysuser.mobile,
            #     "company": position.company_name,
            #     "position": position.title,
            #     "ip": self.request.remote_ip,
            #     "sys": 1
            # })
            #
            # result = RandCode().send_new_appliacation_to_applier(data)
            pass


    @gen.coroutine
    def opt_send_recommender_msg(self, recommend_user_id, current_user, position,profile):
        """
        向推荐人发送消息模板
        :param recommend_user_id:
        :param current_user:
        :param position:
        :param profile:
        :return:
        """

        recom_record = yield self.candidate_recom_record_ds.get_candidate_recom_record(conds={
            "position_id": position.id,
            "presentee_user_id": current_user.sysuser.id,
            "post_user_id": recommend_user_id,
        }, appends=["LIMIT 1"])

        work_exp_years = self.profile_ps.calculate_workyears(profile.get("workexps", []))
        job = self.profile_psd.get_job_for_application(profile)
        recent_job = job.get("company_name", "")

        link = make_url(path.EMPLOYEE_RECOMMENDS, host=self.settings.platform_host, wechat_signature=current_user.wechat.signature)

        self.logger.debug("[opt_send_recommender_msg]link:{}".format(link))

        if recom_record and current_user.recom.id:
            application_notice_to_recommender_tpl(current_user.wechat.id,
                                                  current_user.recom.openid,
                                                  link,
                                                  current_user.sysuser.name or current_user.sysuser.nickname,
                                                  position.title,
                                                  work_exp_years,
                                                  recent_job)
#
    @gen.coroutine
    def opt_update_candidate_recom_records(self, apply_id, current_user, recommend_user_id, position):
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
                },fields={
                    "app_id": apply_id
                }
            )
#
    @gen.coroutine
    def opt_hr_msg(self, current_user, profile, position):

        # 1. 向 HR 发送消息模板通知，短信
        if position.publisher:
            work_exp_years = self.profile_ps.calculate_workyears(profile.get("workexps", []))
            job = self.profile_psd.get_job_for_application(profile)
            recent_job = job.get("company_name", "")

            hr_info = yield self.user_hr_account_ds.get_hr_account(conds={
                "id": position.publisher
            })
            is_ok = False
            if hr_info.wxuser_id:
                hr_wxuser = yield self.user_wx_user_ds.get_wxuser(conds={
                    "id": hr_info.wxuser_id,
                    "wechat_id": self.settings.helper_wechat_id,
                })

                is_ok = application_notice_to_hr_tpl(self.settings.helper_wechat_id,
                                             hr_wxuser.openid,
                                             hr_info.name or hr_wxuser.nickname,
                                             position.title,
                                             current_user.sysuser.name or current_user.sysuser.nickname,
                                             work_exp_years,
                                             recent_job)

            if not is_ok:
                # 消息模板发送失败时，只对普通客户发送短信
                if hr_info.mobile and hr_info.account_type == 2:
                    pass
                    #
                    # data = ObjectDict({
                    #     "mobile": mobile,
                    #     "position": position.title,
                    #     "ip": self.request.remote_ip,
                    #     "sys": 1
                    # })
                    # result = RandCode().send_new_application_to_hr(data)


        # 2. 向 HR 发送邮件通知
        # TODO
