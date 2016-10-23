# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common import ObjectDict
from util.tool.url_tool import make_url
import conf.path as path_const
import conf.message as msg_const
import conf.common as const


class LoginHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        """渲染 login 页面模板"""
        _mobile = ""
        _code = "86"

        # TODO 注册和忘记密码 url 码暂时走老微信
        _register_url = make_url(
            path_const.PATH_AUTH,
            self.params,
            m="check",
            method="register")
        _forget_pass_url = make_url(
            path_const.PATH_AUTH,
            self.params,
            m="check",
            method="reset_password")

        data = ObjectDict(
            mobile=_mobile,
            code=_code,
            links=dict(
                forget_pass_url=_forget_pass_url,
                register_url=_register_url
            )
        )
        self.render_page("/system/login.html", data=data)

    @gen.coroutine
    def post(self):
        """登录操作， api 请求"""
        try:
            self.guarantee('username', 'password', 'next_url')
        except AttributeError:
            return

        res = yield self.user_ps.login_by_mobile_pwd(
            self.params.username, self.params.password)
        if res.status == msg_const.SUCCESS:
            userinfo = ObjectDict(res.data)

            if userinfo.unionid:
                self._build_session_by_unionid(userinfo.unionid)
                self.redirect(self.params.next_url)
                return

        self.send_json(
            status_code=msg_const.FAILURE,
            message=msg_const.LOGIN_FAILURE,
            data={})
