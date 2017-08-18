# coding=utf-8

from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated, \
    check_and_apply_profile

class ApplicationHandler(BaseHandler):

    @handle_response
    @check_and_apply_profile
    @authenticated
    @gen.coroutine
    def get(self):

        # 判断职位相关状态是否合规
        position = yield self.position_ps.get_position(self.params.pid)
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

            result, _, _ = yield self.application_ps.check_custom_cv(
                    self.current_user, position, custom_cv_tpls)

            if not result:
                p = {
                    'pid':self.params.pid,
                    'wechat_signature': self.params.wechat_signature
                }
                if self.params.recom:
                    p['recom'] = self.params.recom
                self.redirect(self.make_url(path.PROFILE_CUSTOM_CV, **p))

                return

        # 定制化需求
        # 雅诗兰黛直接投递
        is_esteelauder = yield self.customize_ps.create_esteelauder_apply(
            position.company_id, position.app_cv_config_id)

        # 跳转到 profile get_view, 传递 apply 和 pid
        self.redirect(self.make_url(path.PROFILE_PREVIEW,
                               self.params,
                               is_skip="1" if is_esteelauder else "0"))

    @handle_response
    @check_and_apply_profile
    @authenticated
    @gen.coroutine
    def post(self):
        """ 处理普通申请 """

        self.logger.warn("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& post application api begin &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        pid = self.json_args.pid
        position = yield self.position_ps.get_position(pid)

        self.logger.warn(pid)
        self.logger.warn(position)

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

            result, _, _ = yield self.application_ps.check_custom_cv(
                    self.current_user, position, custom_cv_tpls)

            self.logger.warn("result: %s" % result)

            if not result:
                self.send_json_error(
                    data=dict(next_url=self.make_url(path.PROFILE_CUSTOM_CV, pid=pid, wechat_signature=self.params.wechat_signature)),
                    message='')
                return

        is_applied, message, apply_id = yield self.application_ps.create_application(
            position, self.current_user, is_platform=self.is_platform, has_recom='recom' in self.params)

        # TODO (tangyiliang) 申请后操作，以下操作全部可以走消息队列
        if is_applied:

            # 1. 添加积分
            yield self.application_ps.opt_add_reward(apply_id, self.current_user)

            # 2. 向求职者发送消息通知（消息模板，短信）
            yield self.application_ps.opt_send_applier_msg(
                apply_id, self.current_user, position, self.is_platform)

            # 3. 向推荐人发送消息模板
            recommender_user_id, _, _ = yield self.application_ps.get_recommend_user(
                self.current_user, position, self.is_platform)

            if recommender_user_id:
                yield self.application_ps.opt_send_recommender_msg(
                    recommender_user_id, self.current_user, position)

                # 4. 更新挖掘被动求职者信息
                yield self.application_ps.opt_update_candidate_recom_records(
                    apply_id, self.current_user, recommender_user_id, position)

            # 5. 向 HR 发送消息通知（消息模板，短信，邮件）
            yield self.application_ps.opt_hr_msg(
                apply_id, self.current_user, position, self.is_platform)

            # 定制化
            # 宝洁投递后，跳转到指定页面
            message = yield self.customize_ps.get_pgcareers_msg(
                self.current_user.wechat.company_id)

            self.send_json_success(data=dict(apply_id=apply_id),
                                   message=message)

            # 发送转发申请红包
            if self.json_args.recom:
                yield self.redpacket_ps.handle_red_packet_position_related(
                    self.current_user,
                    position,
                    redislocker=self.redis,
                    is_apply=True,
                    psc=self.json_args.psc)

        else:
            self.send_json_error(message=message)


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

        position = yield self.position_ps.get_position(self.params.pid)
        if self.params.pid and position.email_resume_conf == 0:
            # 职位必须能接受Email投递 而且params含有pid
            create_status, message = yield self.application_ps.create_email_apply(self.params, position, self.current_user, self.is_platform)
            if not create_status:
                # 职位不能申请, 直接返回不能再次redirect
                self.send_json_error(message=message)
                return
        else:
            self.logger.debug("Start to create email profile..")
            yield self.application_ps.create_email_profile(self.params, self.current_user, self.is_platform)

        # 置空不必要参数，避免在 make_url 中被用到
        self.params.pop("name", None)

        self.redirect(self.make_url(path.APPLICATION_EMAIL, self.params, confirm="1"))
