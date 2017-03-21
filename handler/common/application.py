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
from util.common.decorator import handle_response, authenticated, verified_mobile_oneself, check_and_apply_profile
from util.tool.json_tool import encode_json_dumps
from util.tool.url_tool import make_url


class ApplicationHandler(BaseHandler):

    @handle_response
    @check_and_apply_profile
    @gen.coroutine
    def get(self):
        # 获得职位信息

        # 判断职位相关状态是否合规
        position = yield self.position_ps.get_position(self.params.pid)
        check_status, message = yield self.application_ps.check_position(
            position, self.current_user)
        self.logger.debug("[create_reply]check_status:{}, message:{}".format(check_status, message))

        if not check_status:
            self.render(
                template_name='refer/weixin/systemmessage/successapply.html',
                message=message,
                nexturl=make_url(path.POSITION_LIST, self.params,
                                 escape=['next_url', 'pid']))
            return

        # 如果是自定义简历职位
        # 检查该 profile 是否符合自定义简历必填项,
        # 如果不符合的话跳转到自定义简历填写页
        if position.app_cv_config_id:
            # 读取自定义字段 meta 信息
            custom_cv_tpls = yield self.profile_ps.get_custom_tpl_all()
            # -> formats of custom_cv_tpls is like:
            # [{"field_name1": "map1"}, {"field_name2": "map2"}]

            result, resume_dict, json_config = yield self.application_ps.check_custom_cv(
                self.current_user, position, custom_cv_tpls)

            if not result:
                self.render('refer/weixin/application/app_cv_conf.html',
                            resume=encode_json_dumps(resume_dict),
                            cv_conf=encode_json_dumps(json_config))
                return

        # 定制化需求
        # 雅诗兰黛直接投递
        is_esteelauder = yield self.customize_ps.create_esteelauder_apply(
            position.company_id, position.app_cv_config_id)
        is_skip = "1" if is_esteelauder else "0"

        # 跳转到 profile get_view, 传递 apply 和 pid
        self.redirect(make_url(path.PROFILE_PREVIEW, self.params, is_skip=is_skip))

    @handle_response
    # @verified_mobile_oneself
    @check_and_apply_profile
    @authenticated
    @gen.coroutine
    def post(self):
        """ 处理普通申请 """

        position = yield self.position_ps.get_position(self.json_args.pid)

        is_applied, message, apply_id = yield self.application_ps.create_application(
            {},
            position,
            self.current_user)
        self.logger.debug("[post_apply]is_applied:{}, message:{}, appid:{}".format(is_applied, message, apply_id))

        if is_applied:
            # 如果是自定义职位，入库 job_resume_other
            # 暂时不接其返回值
            yield self.application_ps.save_job_resume_other(
                self.current_user.profile, apply_id, position)

            # 定制化
            # 宝洁投递后，跳转到指定页面
            message = yield self.customize_ps.get_pgcareers_msg(self.current_user.wechat.company_id)

            self.send_json_success(
                data=dict(apply_id=apply_id),
                message=message)
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

        self.logger.debug("update_candidate_company:{}".format(res))

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
            self.logger.debug(u"Start to create email profile..")
            yield self.application_ps.create_email_profile(self.params, self.current_user, self.is_platform)

        # 置空不必要参数，避免在 make_url 中被用到
        self.params.pop("name", None)
        self.params.pop("email", None)

        self.redirct(make_url(path.APPLICATION_EMAIL, self.params, confirm="1"))
