# coding=utf-8

from tornado import gen

from schematics.validate import DataError

from util.common import ObjectDict

import conf.message as msg
import conf.path as path
import conf.common as const

from handler.base import BaseHandler
from cache.user.passport_session import PassportCache
from util.common.decorator import handle_response, authenticated
from util.tool.str_tool import to_str, password_validate
from util.tool.date_tool import curr_now
from util.common.cipher import encode_id

from handler.common.captcha import CaptchaMixin
from domain.user import UserCreationForm


class LoginHandler(BaseHandler):
    """用户登录"""

    @handle_response
    @gen.coroutine
    def get(self):
        """渲染 login 页面模板"""

        data = ObjectDict(
            mobile=""
        )
        self.render_page("system/login.html", data=data)

    @handle_response
    @gen.coroutine
    def post(self):
        """登录操作， api 请求"""

        try:
            self.guarantee("mobile", "password", "country_code")
        except AttributeError:
            return

        res = yield self.usercenter_ps.post_login(params={
            "countryCode": self.params.country_code,
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
        else:
            self.send_json_error(message=res.message)


class LogoutHandler(BaseHandler):
    """
    用户登出.
    """

    @authenticated
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
        # 清除公众号，仟寻下的用户 session
        pass_session.clear_session(session_id, self.current_user.wechat.id)
        pass_session.clear_session(session_id, self.settings.qx_wechat_id)
        self.clear_all_cookies()

        if self.is_platform:
            redirect_url = self.make_url(path.POSITION_LIST, params=self.params, escape=['next_url', 'pid'])
        else:
            redirect_url = self.make_url(path.GAMMA_POSITION, params=self.params, escape=['next_url', 'pid'])
        self.redirect(redirect_url)


class RegisterHandler(CaptchaMixin, BaseHandler):
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
    def post(self, method):

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
            national_code=1,
            code_type=1  # 指定为忘记密码类型，提交手机号时需要
        )
        self.render_page("system/auth_check_mobile.html",
                         data=data, meta_title=const.PAGE_FORGET_PASSWORD)

    @handle_response
    @gen.coroutine
    def get_register(self):
        """正常注册"""

        data = ObjectDict(
            headimg="",
            code_type=0  # 指定为正常注册类型，提交手机号时需要
        )
        self.render_page("system/auth_check_mobile.html",
                         data=data, meta_title=const.PAGE_REGISTER)

    @handle_response
    @gen.coroutine
    def get_code(self):
        """填写验证码"""

        mobile = to_str(self.get_secure_cookie(const.COOKIE_MOBILE_REGISTER))
        code_type = int(self.params.code_type)

        site_title = const.PAGE_REGISTER
        if code_type == 1:
            # 忘记密码
            site_title = const.PAGE_FORGET_PASSWORD

        data = ObjectDict(
            country_code=self.params.country_code,
            mobile=mobile,
            code_type=code_type
        )
        self.render_page("system/register.html",
                         data=data, meta_title=site_title)

    @handle_response
    @gen.coroutine
    def get_setpasswd(self):
        """设置密码"""
        code_type = int(self.params.code_type)
        mmc = self.params._mmc or ""
        site_title = const.PAGE_REGISTER

        if code_type == 1:
            # 忘记密码
            site_title = const.PAGE_FORGET_PASSWORD

        data = ObjectDict(
            code_type=code_type,  # 指定为设置密码的类型
            _mmc=mmc
        )
        self.render_page("system/auth_set_passwd.html", data=data, meta_title=site_title)

    @handle_response
    @gen.coroutine
    def post_mobile(self):
        """提交手机号，获得验证码"""

        try:
            self.guarantee("mobile", "code_type", "country_code", "vcode")
        except AttributeError:
            return

        self.logger.debug("vcode: %s" % self.params.vcode)

        if not self.params.vcode:
            self.send_json_error(message=msg.VCODE_NOT_EXIST)
            return

        session_id = to_str(
            self.get_secure_cookie(const.COOKIE_SESSIONID) or
            self.get_secure_cookie(const.COOKIE_MVIEWERID) or ''
        )

        result = self.captcha_check(session_id, self.current_user.sysuser.id,
                                    self.params.vcode)

        if not result:
            self.send_json_error(message=msg.VCODE_INVALID)
            return

        ret = yield self.usercenter_ps.post_ismobileregistered(
            country_code=self.params.country_code, mobile=self.params.mobile)

        if self.params.code_type == 1:
            # 忘记密码
            if ret.status != const.API_SUCCESS or not ret.data.exist:
                # 手机号不存在，无法修改密码
                self.send_json_error(message=msg.CELLPHONE_INVALID_MOBILE)
                raise gen.Return()
            valid_type = const.MOBILE_CODE_OPT_TYPE.forget_password

        else:
            # 普通注册
            if ret.status != const.API_SUCCESS or ret.data.exist:
                # 手机号已存在，不能再注册新用户
                self.send_json_error(message=msg.CELLPHONE_MOBILE_HAD_REGISTERED)
                raise gen.Return()

            valid_type = const.MOBILE_CODE_OPT_TYPE.code_register

        result = yield self.cellphone_ps.send_valid_code(
            country_code=self.params.country_code,
            mobile=self.params.mobile,
            type=valid_type
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
        else:
            self.set_secure_cookie(const.COOKIE_MOBILE_REGISTER, self.params.mobile, expires_days=0.1, httponly=True)
            self.set_secure_cookie(const.COOKIE_COUNTRY_CODE_REGISTER, self.params.country_code, expires_days=0.1,
                                   httponly=True)

            self.send_json_success(data={
                "mobile": self.params.mobile,
                "code_type": self.params.code_type
            })

    @handle_response
    @gen.coroutine
    def post_code(self):
        """提交验证码，检查手机号是否有效"""

        try:
            self.guarantee("mobile", "code", "code_type", "country_code")
        except AttributeError:
            return

        if self.params.code_type == 1:
            # 忘记密码
            valid_type = const.MOBILE_CODE_OPT_TYPE.forget_password
        else:
            # 普通注册
            valid_type = const.MOBILE_CODE_OPT_TYPE.code_register

        # 验证验证码
        verify_response = yield self.cellphone_ps.verify_mobile(
            self.params.country_code,
            self.params.mobile, self.params.code, valid_type
        )
        if verify_response.status != const.API_SUCCESS:
            self.send_json_error(message=verify_response.message)
            raise gen.Return()
        elif verify_response.data == const.NO:
            self.send_json_error(message=msg.CELLPHONE_INVALID_CODE)
            raise gen.Return()
        else:
            # 返回加密的 code 值，供前端拼接 url，以验证用户重要操作是否已经验证手机号
            self.send_json_success(data={
                "_mmc": encode_id(int(self.params.mobile), 8),
                "code_type": self.params.code_type
            })

    @handle_response
    @gen.coroutine
    def post_setpasswd(self):
        """提交设置的密码

        code_type: 0 -> 手机浏览器创建用户
                   1 -> 微信中或手机浏览器中重置密码
        """

        try:
            self.guarantee("password", "repassword", "code_type")
        except AttributeError:
            raise gen.Return()

        if self.params.password != self.params.repassword:
            self.send_json_error(message=msg.CELLPHONE_REGISTER_PASSWD_NOT_MATCH)
            raise gen.Return()

        mobile = self.get_secure_cookie(const.COOKIE_MOBILE_REGISTER)
        country_code = self.get_secure_cookie(const.COOKIE_COUNTRY_CODE_REGISTER)

        url_mobile = self.params._mmc

        # 判断前后的mobile相等且包含 country_code
        if (not mobile or
            not url_mobile or
            encode_id(int(mobile), 8) != url_mobile or
            not country_code):
            self.send_json_error(message=msg.CELLPHONE_MOBILE_SET_PASSWD_FAILED)
            raise gen.Return()

        if not password_validate(self.params.password):
            self.send_json_error(message=msg.CELLPHONE_PASSWORD_ERROR)
            raise gen.Return()

        # 忘记密码
        if self.params.code_type == 1:
            res = yield self.usercenter_ps.post_resetpassword(country_code, mobile, self.params.password)
            if res.status != const.API_SUCCESS:
                self.send_json_error(message=res.message)
                raise gen.Return()
        else:
            # 开始创建 user 对象
            user_form = UserCreationForm({
                'country_code': country_code,
                'password': self.params.password,
                'mobile': int(mobile),
                'username': mobile,
                'register_ip': self.remote_ip,
                'register_time': curr_now()
            })
            try:
                user_form.validate()
            except DataError:
                self.send_json_error(message=msg.CELLPHONE_REGISTER_FAILED)
                return

            self.logger.debug("[user creation] user_form: %s" % user_form.to_primitive())

            res = yield self.usercenter_ps.post_register(user_form)
            if res.status != const.API_SUCCESS:
                self.send_json_error(message=msg.CELLPHONE_REGISTER_FAILED)
                return

            # 设置登录cookie
            session_id = self._make_new_session_id(res.data.user_id)
            self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True)

        next_url = self.json_args.get("next_url", "")
        self.send_json_success(data={
            "next_url": next_url
        })


class SendValidCodeHandler(BaseHandler):
    """发送手机验证码，不需要图片验证码的页面使用"""

    @handle_response
    @gen.coroutine
    def post(self):

        mobile = self.json_args.mobile
        if not mobile:
            mobile = self.redis.get(
                const.CONFIRM_REFERRAL_MOBILE.format(self.json_args.rkey, self.current_user.sysuser.id)).get("mobile")
        # 校验手机号是否已经被注册
        ret = yield self.usercenter_ps.post_ismobileregistered(mobile=mobile)
        if ret.status != const.API_SUCCESS or ret.data.exist:
            # 手机号已存在，不能再注册新用户
            self.send_json_error(message=msg.CELLPHONE_MOBILE_HAD_REGISTERED)
            return

        if self.params.mobile_code_type == "change_mobile":
            valid_type = const.MOBILE_CODE_OPT_TYPE.change_mobile
        else:
            valid_type = const.MOBILE_CODE_OPT_TYPE.referral_confirm
        # valid_type = const.MOBILE_CODE_OPT_TYPE.referral_confirm
        result = yield self.cellphone_ps.send_valid_code(
            mobile=mobile,
            type=valid_type
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
        else:
            self.send_json_success()
