# coding=utf-8

from tornado import gen
from util.common import ObjectDict

import conf.path as path
import conf.common as const
from handler.base import BaseHandler
from cache.user.passport_session import PassportCache
from util.common.decorator import handle_response, verified_mobile_oneself
from util.tool.str_tool import to_str
from util.tool.url_tool import make_url


class LoginHandler(BaseHandler):
    """用户登录"""

    @handle_response
    @gen.coroutine
    def get(self):
        """渲染 login 页面模板"""

        data = ObjectDict(
            mobile="",
            national_code_tpl=const.NATIONAL_CODE,
            national_code=1 # 目前只支持中国大陆手机号注册
        )
        self.render_page("system/login.html", data=data)

    @handle_response
    @gen.coroutine
    def post(self):
        """登录操作， api 请求"""

        try:
            self.guarantee("mobile", "password", "national_code")
        except AttributeError:
            return

        res = yield self.usercenter_ps.post_login(params={
            "mobile": self.params.mobile,
            "password": self.params.password,
        })

        next_url = self.json_args.get("next_url", "")

        if res.status == const.API_SUCCESS:
            session_id = self._make_new_session_id(res.data.user_id)
            self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True)
            self.send_json_success(data={
                "next_url": next_url
            })
            raise gen.Return()
        else:
            self.send_json_error()


class LogoutHandler(BaseHandler):
    """
    用户登出.
    """

    @handle_response
    @gen.coroutine
    def get(self):
        """
        登出操作，登出后跳转到职位列表页.
        """
        yield self.usercenter_ps.post_logout(self.current_user.sysuser.id)

        session_id = to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        self.clear_cookie(name=const.COOKIE_SESSIONID)
        pass_session = PassportCache()
        pass_session.clear_session(session_id, self.current_user.wechat.id)
        redirect_url = make_url(path.POSITIONLIST_PATH, params=self.params, escape=['next_url'])
        self.redirect(redirect_url)
        raise gen.Return()

class RegisterHandler(BaseHandler):
    """用户注册"""

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
    def get(self, method):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def get_forgetpasswd(self):
        """忘记密码"""

        data = ObjectDict(
            headimg="",
            national_code_tpl=const.NATIONAL_CODE,
            national_code=1, # 目前只支持中国大陆手机号注册
            code_type=1 # 指定为忘记密码类型，提交手机号时需要
        )
        self.render_page("system/auth_check_mobile.html", data=data, site_title=const.PAGE_FORGET_PASSWORD)

    @handle_response
    @gen.coroutine
    def get_register(self):
        """正常注册"""

        data = ObjectDict(
            headimg="",
            national_code_tpl=const.NATIONAL_CODE,
            national_code=1, # 目前只支持中国大陆手机号注册
            code_type=0 # 指定为正常注册类型，提交手机号时需要
        )
        self.render_page("system/auth_check_mobile.html", data=data, site_title=const.PAGE_REGISTER)

    @handle_response
    @gen.coroutine
    def post_mobile(self):
        """提交手机号，获得验证码"""

        try:
            self.guarantee("mobile", "code_type", "national_code")
        except AttributeError:
            return

        if self.params.code_type == 1:
            # 忘记密码
            valid_type = const.MOBILE_CODE_OPT_TYPE.code_register
        else:
            valid_type = const.MOBILE_CODE_OPT_TYPE.forget_password

        result = yield self.cellphone_ps.send_valid_code(
            self.params.mobile,
            valid_type
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
        else:
            self.send_json_success(data={
                "code_type": self.params.code_type
            })


    @handle_response
    @gen.coroutine
    def post_check(self):
        """提交验证码，检查是否注册成功"""

        try:
            self.guarantee("mobile", "code", "national_code")
        except AttributeError:
            return
