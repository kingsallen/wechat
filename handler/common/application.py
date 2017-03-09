# coding=utf-8

# @Time    : 3/6/17 10:55
# @Author  : panda (panyuxin@moseeker.com)
# @File    : application.py
# @DES     :

from tornado import gen

import conf.path as path
import conf.common as const
import conf.message as msg

from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated, verified_mobile_oneself
from util.tool.json_tool import encode_json_dumps
from util.tool.url_tool import make_url


class ApplicationHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, method):
        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'get_' + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def post(self, method):
        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @authenticated
    @gen.coroutine
    def get_app(self):

        position = yield self.position_ps.get_position(self.params.pid)
        check_status, message = self.check_position(position, self.current_user)
        self.logger.debug("[create_email_reply]check_status:{}, message:{}".format(check_status, message))
        if not check_status:
            self.render('weixin/systemmessage/successapply.html',
                           message=message,
                           nexturl=make_url(path.POSITION_LIST, self.params, escape=['next_url', 'pid']))
            raise gen.Return()

        # 判断 current_user 的 profile 是否符合要求
        # 1. 获取 profile
        has_profile, profile = yield self.profile_ps.has_profile(self.current_user.sysuser.id)

        # 2. 如果没有 profile 按照规则跳转
        if not has_profile:
            # TODO 与 profile 共用
            no_profile_redirection(self.params.pid)
            return

        # 3. 如果有 profile 但是是自定义职位,
        #    检查该 profile 是否符合自定义简历必填项,
        #        如果不符合的话跳转到自定义简历填写页
        if position.app_cv_config_id:
            is_true, resume_dict, json_config = yield self.application_ps.custom_check_failure_redirection(profile, position, self.current_user.sysuser)
            if is_true:
                self.render('weixin/application/app_cv_conf.html',
                            resume=encode_json_dumps(resume_dict),
                            cv_conf=encode_json_dumps(json_config))
                return

        # 定制化需求
        # 雅诗兰黛直接投递
        is_esteelauder = yield self.customize_ps.create_esteelauder_apply(position.company_id, position.app_cv_config_id)
        is_skip = "1" if is_esteelauder else "0"

        # 跳转到 profile get_view, 传递 apply 和 pid
        # TODO 缺少 profile 路由
        self.redirect(make_url(const.PROFILE_URL, self.params,
                               apply="1", is_skip=is_skip))

    @handle_response
    @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def post_create_email(self):
        """
        处理 Email 投递
        :return:
        """
        # 更新姓名，邮箱信息
        yield self.usercenter_ps.update_user(self.current_user.sysuser.id, params={
            "name": self.current_user.sysuser.name or self.params.name.strip(),
            "email": self.current_user.sysuser.email or self.params.email.strip()
        })

        # 候选人信息更新
        yield self.application_ps.update_candidate_company(self.params.name, self.current_user.sysuser.id)

        position = yield self.position_ps.get_position(self.params.pid)
        if self.params.pid and position.email_resume_conf == 0:
            # 职位必须能接受Email投递 而且params含有pid
            self.logger.debug("[post_create_email]Start to create email application..")
            create_status, message = yield self.application_ps.create_email_apply(self.params, position, self.current_user, self.is_platform)
            self.logger.debug("[post_create_email]create_status:{}, message:{}".format(create_status, message))
            if not create_status:
                # 职位不能申请, 直接返回不能再次redirect
                self.send_json_error(message=message)
                return
        else:
            self.LOG.debug(u"Start to create email profile..")
            yield self.application_ps.create_email_profile(self.params, self.current_user, self.is_platform)

        self.render("weixin/sysuser/emailresume_sent.html")

    @handle_response
    @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def post_apply(self):
        """
        处理普通申请
        :return:
        """

        is_applied, message, apply_id = yield self.position_ps.get_position(self.params.pid)
        self.logger.debug("[post_apply]is_applied:{}, message:{}, appid:{}".format(is_applied, message, apply_id))
        if is_applied:
            # 定制化
            # 宝洁投递后，跳转到指定页面
            message = yield self.customize_ps.get_pgcareers_msg(self.current_user.wechat.company_id)
            if message:
                nexturl = make_url(path.POSITION_LIST, params=self.params, escape=['next_url', 'pid'])
                self.render('weixin/systemmessage/successapply.html', message=message, nexturl=nexturl)
            else:
                self.redirect(make_url(path.USERCENTER_APPLYRECORD.format(apply_id), self.params, escape=['next_url', 'pid']))
        else:
            self.send_json_error(message=message)
