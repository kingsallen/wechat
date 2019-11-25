# coding=utf-8

import uuid
from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated, \
    check_and_apply_profile
from util.common.cipher import decode_id
from util.common.mq import jd_apply_publisher
from util.common import ObjectDict
import conf.message as msg
from util.tool.url_tool import make_static_url
from util.tool.date_tool import curr_now


class ApplicationHandler(BaseHandler):
    @handle_response
    @check_and_apply_profile
    @authenticated
    @gen.coroutine
    def get(self):

        # 判断职位相关状态是否合规
        position = yield self.position_ps.get_position(self.params.pid, display_locale=self.get_current_locale())
        check_status, message = yield self.application_ps.check_position(
            position, self.current_user)

        if not check_status:
            self.render(
                template_name='refer/weixin/systemmessage/successapply.html',
                message=message,
                nexturl=self.make_url(path.POSITION_LIST, self.params, escape=['next_url', 'pid']))
            return

        # 如果是自定义简历职位
        # 检查该 profile 是否符合自定义简历必填项,
        # 如果不符合的话跳转到自定义简历填写页
        if position.app_cv_config_id:
            # 读取自定义字段 meta 信息
            custom_cv_tpls = yield self.profile_ps.get_custom_tpl_all()
            # -> formats of custom_cv_tpls is like:
            # [{"field_name1": "map1"}, {"field_name2": "map2"}]

            # result = yield self.application_ps.check_custom_cv_v2(
            #     self.current_user.sysuser.id, position.id)

            # if not result:
            self.redirect(self.make_url(path.PROFILE_CUSTOM_CV, self.params))
            return

        # 定制化需求
        # 直接投递
        is_direct_apply = yield self.customize_ps.create_direct_apply(
            position.company_id, position.app_cv_config_id)

        # 跳转到 profile get_view, 传递 apply 和 pid
        self.redirect(
            self.make_url(path.PROFILE_PREVIEW, self.params, is_skip="1" if is_direct_apply else "0")
        )

    @handle_response
    @check_and_apply_profile
    @authenticated
    @gen.coroutine
    def post(self):
        """ 处理普通申请 """

        self.logger.warn(
            "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& post application api begin &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

        pid = self.json_args.pid

        # 联系内推： 候选人填写简历信息 确认提交，此时并没有真正投递要等到员工完成推荐评价才算是真正投递
        if self.params.contact_referral:
            # 申请来自哪里
            origin = 2 if self.params.invite_apply == str(const.YES) else 1
            if self.params.root_recomd:
                recom = decode_id(self.params.root_recomd)
                psc = -1
            else:
                recom = decode_id(self.json_args.recom)
                psc = self.json_args.psc if self.json_args.psc else 0
            ret = yield self.user_ps.if_referral_position(
                self.current_user.company.id,
                recom, psc, pid, self.current_user.sysuser.id)
            if not ret.status == const.API_SUCCESS:
                self.send_json_error(message=ret.message)
                return
            root_user_id = ret.data.get('user', {}).get('uid', 0)
            yield self.user_ps.referral_confirm_submit(
                self.current_user.company.id, self.current_user.sysuser.id, root_user_id, pid, origin)
            self.track("cReferralAddProfile")
            self.send_json_success(
                data=dict(next_url=self.make_url(path.REFERRAL_CONTACT_RESULT, self.params),
                          message=''))
            return

        self.log_info = {"position_id": pid}
        position = yield self.position_ps.get_position(pid, display_locale=self.get_current_locale())

        self.logger.warn(pid)
        self.logger.warn(position)
        suppress_apply = self.customize_ps.get_suppress_apply(position)
        if suppress_apply.get("is_suppress_apply"):
            self.send_json_error(message="请前往诺华集团官网进行投递")
            return

        check_status, message = yield self.application_ps.check_position(
            position, self.current_user)
        self.logger.debug("[create_reply]check_status:{}, message:{}".format(check_status, message))
        if not check_status:
            self.send_json_error(message=message)
            return

        if position.app_cv_config_id:
            self.logger.warn("position.app_cv_config_id: %s" % position.app_cv_config_id)

            # 读取自定义字段 meta 信息
            custom_cv_tpls = yield self.profile_ps.get_custom_tpl_all()
            # -> formats of custom_cv_tpls is like:
            # [{"field_name1": "map1"}, {"field_name2": "map2"}]

            result = yield self.application_ps.check_custom_cv_v2(
                self.current_user.sysuser.id, position.id)

            if not result:
                self.send_json_error(
                    data=dict(next_url=self.make_url(path.PROFILE_CUSTOM_CV, self.params, pid=position.id),
                              message=''))
                return

        is_applied, message, apply_id = yield self.application_ps.create_application(
            position,
            self.current_user,
            self.params,
            is_platform=self.is_platform,
            has_recom='recom' in self.params,
            source=self.params.source
        )

        # TODO (tangyiliang) 申请后操作，以下操作全部可以走消息队列
        if is_applied:

            # 申请红包
            message = {"name": const.APPLY_MQ_NAME,
                       "ID": str(uuid.uuid4()),
                       "recommend_user_id": self.current_user.recom.id if self.current_user.recom else 0,
                       "applier_id": self.current_user.sysuser.id,
                       "position_id": position.id,
                       "apply_time": curr_now(),
                       "company_id": self.current_user.company.id,
                       "application_id": apply_id,
                       "psc": self.json_args.psc or 0
                       }
            self.logger.debug("[hb]----send retransmit apply redpacket")
            jd_apply_publisher.publish_message(message=message, routing_key="retransmit_apply_exchange.redpacket")

            # 绑定application与pre_share_chain
            if self.json_args.psc or self.current_user.recom:
                yield self.application_ps.bind_app_chain_info(apply_id, psc_id=self.json_args.psc, direct_referral_user_id=self.current_user.recom.id if self.current_user.recom else 0)

            # 添加积分
            yield self.application_ps.opt_add_reward(apply_id, self.current_user)

            # 更新挖掘被动求职者信息
            recommender_user_id, _, _, depth = yield self.application_ps.get_recommend_user(
                self.current_user, position, self.is_platform)

            # 神策埋点
            self._add_sensor_track(depth, recommender_user_id)

            if recommender_user_id:
                yield self.application_ps.opt_update_candidate_recom_records(
                    apply_id, self.current_user, recommender_user_id, position)

            # 定制化
            # 宝洁投递后，跳转到指定页面
            message = yield self.customize_ps.get_pgcareers_msg(
                self.current_user.wechat.company_id)

            self.send_json_success(data=dict(apply_id=apply_id),
                                   message=message)

        else:
            self.send_json_error(message=message)

    def _add_sensor_track(self, depth, recommender_user_id):
        if self.params.promote == const.PROMOTE:
            origin = const.SA_ORIGIN_PROMOTE
        elif self.params.source == const.FANS_RECOMMEND:
            origin = const.SA_ORIGIN_FANS_RECOMMEND
        elif self.params.invite_apply == str(const.YES):
            origin = const.SA_ORIGIN_APPLICATION_INVITE
        elif recommender_user_id:
            origin = const.SA_ORIGIN_EMPLOYEE_SHARE
        else:
            origin = const.SA_ORIGIN_PLATFORM
        if self.params.invite_apply == str(const.YES):
            self.track("inDirectReferral", properties={"apply_origin": const.SA_INDIRECT_REFERRAL_INVITE})
        self.track("cApplySuccess", properties={"origin": origin, "depth": depth})


class ApplicationEmailHandler(BaseHandler):
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """Email 信息填写页面和确认页面"""

        if self.params.confirm:
            self.render(template_name="refer/weixin/sysuser/emailresume_sent.html")
        else:
            self.render_page(template_name="profile/email-input.html", data={
                "mobile_valid": self.current_user.sysuser.username == str(self.current_user.sysuser.mobile)
            })

    @handle_response
    # @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def post(self):
        """
        处理 Email 投递
        :return:
        """
        # 更新姓名，邮箱信息
        res = yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
            "name": self.current_user.sysuser.name or self.params.name.strip(),
            "email": self.current_user.sysuser.email or self.params.email.strip()
        })

        self.logger.debug("update_user:{}".format(res))

        # 候选人信息更新
        res = yield self.application_ps.update_candidate_company(self.params.name, self.current_user.sysuser.id)

        position = yield self.position_ps.get_position(self.params.pid, display_locale=self.get_current_locale())
        # 职位必须能接受Email投递 而且params含有pid
        self.current_user.company.logo = make_static_url(self.current_user.company.logo, protocol="https", ensure_protocol=True)
        if self.params.pid and position.email_resume_conf == 0:
            create_status, message = yield self.application_ps.create_email_apply(self.params, position,
                                                                                  self.current_user, self.is_platform, self.params.source)
            if not create_status:
                # 职位不能申请, 直接返回不能再次redirect
                messages = message
                data = ObjectDict(
                    kind=1,  # // {0: success, 1: failure, 10: email}
                    messages=[messages],  # ['hello world', 'abjsldjf']
                    button_text=msg.BACK_CN,
                    button_link=self.make_url(path.POSITION_LIST,
                                              self.params,
                                              host=self.host),
                    jump_link=None  # // 如果有会自动，没有就不自动跳转
                )

                self.render_page(template_name="system/user-info.html",
                                 data=data)
                return
        else:
            self.logger.debug("Start to create email profile..")
            yield self.application_ps.create_email_profile(self.params, self.current_user, self.is_platform)

        # 置空不必要参数，避免在 make_url 中被用到
        self.params.pop("name", None)

        self.redirect(self.make_url(path.APPLICATION_EMAIL, self.params, confirm="1"))
