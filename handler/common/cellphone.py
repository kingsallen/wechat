# coding=utf-8


from tornado import gen

import conf.common as const
import conf.message as msg

from handler.base import BaseHandler
from util.common.decorator import handle_response, common_handler
from util.common import ObjectDict
from util.common.cipher import encode_id

from util.tool.str_tool import password_crypt, to_str

from handler.common.captcha import CaptchaMixin

from thrift_gen.gen.mq.struct.ttypes import SmsType
from util.tool.date_tool import curr_now


@common_handler
class CellphoneBindHandler(CaptchaMixin, BaseHandler):
    """ 发送短信验证码的共通方法
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    不同的业务场景，会有不同的业务逻辑处理
    method 类型: register(type=1),
                forgetpasswd(type=2),
                setpassed(type=3),
                changemobile(type=4)
    """

    @handle_response
    @gen.coroutine
    def get(self, method='register'):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            self.vcode = self.params.vcode
            yield getattr(self, 'get_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def post(self, method='register'):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def get_voice_register(self):
        """语音验证码(限注册)"""
        yield self._opt_get_voice_register_code()

    @handle_response
    @gen.coroutine
    def get_register(self):
        """空帐号补填手机号"""
        self.track("cGetCellphoneCode")
        yield self._opt_get_cellphone_code(const.MOBILE_CODE_OPT_TYPE.code_register)

    @handle_response
    @gen.coroutine
    def get_forgetpasswd(self):
        yield self._opt_get_cellphone_code(const.MOBILE_CODE_OPT_TYPE.forget_password)

    @handle_response
    @gen.coroutine
    def get_certificate(self):
        """只是验证手机号有效性，不判断手机号是否已经注册等其他逻辑"""
        yield self._opt_get_cellphone_code(const.MOBILE_CODE_OPT_TYPE.code_register)

    @handle_response
    @gen.coroutine
    def get_setpassed(self):
        yield self._opt_get_cellphone_code(const.MOBILE_CODE_OPT_TYPE.valid_old_mobile)

    @handle_response
    @gen.coroutine
    def get_changemobile(self):
        yield self._opt_get_cellphone_code(const.MOBILE_CODE_OPT_TYPE.change_mobile)

    @handle_response
    @gen.coroutine
    def get_validmobile(self):
        """部分操作，需要先确定是否为本人操作。要求验证本人手机号"""
        yield self._opt_get_cellphone_code(const.MOBILE_CODE_OPT_TYPE.valid_old_mobile)

    def _check_vocde(self):
        self.logger.debug("vcode: %s" % self.params.vcode)

        if not self.vcode:
            return False, msg.VCODE_NOT_EXIST

        session_id = to_str(
            self.get_secure_cookie(const.COOKIE_SESSIONID) or
            self.get_secure_cookie(const.COOKIE_MVIEWERID) or ''
        )

        result = self.captcha_check(session_id, self.current_user.sysuser.id,
                                    self.vcode)

        if not result:
            return False, msg.VCODE_INVALID

        return True, None

    @gen.coroutine
    def _opt_get_voice_register_code(self):

        result = yield self.cellphone_ps.send_voice_code_for_register(
            self.params.get('mobile')
        )

        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
            return
        else:
            self.send_json_success()

    @gen.coroutine
    def _opt_get_cellphone_code(self, type):

        check_pass, message = self._check_vocde()
        if not check_pass:
            self.send_json_error(message=message)
            return

        mobile = self.params.get('mobile')
        country_code = self.params.get('country_code')

        if not mobile or not country_code:
            self.send_json_error(msg.CELLPHONE_MOBILE_INVALID)
            return

        # 注册时，不需要判断是否为当前用户手机号
        if type != const.MOBILE_CODE_OPT_TYPE.code_register:

            if self.current_user.sysuser.username.isdigit() and \
               self.params.mobile != self.current_user.sysuser.username and \
               self.params.country_code != self.current_user.sysuser.country_code:

                self.send_json_error(message=msg.CELLPHONE_NOT_MATCH)
                raise gen.Return()

        result = yield self.cellphone_ps.send_valid_code(
            country_code=country_code,
            mobile=mobile,
            type=type
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
            return
        else:
            self.send_json_success()

    @handle_response
    @gen.coroutine
    def post_register(self):
        self.track("cVerifyMobile")
        res = yield self._opt_post_cellphone_code(const.MOBILE_CODE_OPT_TYPE.code_register)
        if res:
            self.track("cRegisterSuccess")
            yield self._opt_post_user_account()

    @handle_response
    @gen.coroutine
    def post_forgetpasswd(self):
        yield self._opt_post_cellphone_code(const.MOBILE_CODE_OPT_TYPE.forget_password)

    @handle_response
    @gen.coroutine
    def post_setpassed(self):
        yield self._opt_post_cellphone_code(const.MOBILE_CODE_OPT_TYPE.valid_old_mobile)

    @handle_response
    @gen.coroutine
    def post_certificate(self):
        """只是验证手机号有效性，不判断手机号是否已经注册等其他逻辑"""
        yield self._opt_post_cellphone_code(const.MOBILE_CODE_OPT_TYPE.code_register)

    @handle_response
    @gen.coroutine
    def post_validmobile(self):
        yield self._opt_post_cellphone_code(const.MOBILE_CODE_OPT_TYPE.valid_old_mobile)

    @handle_response
    @gen.coroutine
    def post_changemobile(self):
        res = yield self._opt_post_cellphone_code(const.MOBILE_CODE_OPT_TYPE.change_mobile)
        if res:
            yield self._opt_post_user_account_change()

    @gen.coroutine
    def _opt_post_cellphone_code(self, type):
        """处理验证码是否有效，正确"""
        try:
            self.guarantee('mobile', 'code', 'country_code')
        except:
            raise gen.Return(False)

        # 验证验证码
        verify_response = yield self.cellphone_ps.verify_mobile(
            country_code=self.params.country_code,
            mobile=self.params.mobile,
            code=self.params.code,
            type=type
        )

        if verify_response.status != const.API_SUCCESS:
            self.send_json_error(message=verify_response.message)
            raise gen.Return(False)

        elif verify_response.data == const.NO:
            self.send_json_error(message=msg.CELLPHONE_INVALID_CODE)
            raise gen.Return(False)

        # 返回加密的 code 值，供前端拼接 url，以验证用户重要操作是否已经验证手机号
        self.send_json_success(data={
            "_mc": encode_id(int(self.params.code), 8)
        })

        self.set_secure_cookie(
            const.COOKIE_MOBILE_CODE,
            self.params.code,
            expires_days=0.05,
            httponly=True)

        raise gen.Return(True)

    @gen.coroutine
    def _opt_post_user_account(self):

        # 检查是否需要合并 pc 账号
        if self.current_user.sysuser and \
            str(self.current_user.sysuser.mobile) != str(self.current_user.sysuser.username):

            response = yield self.cellphone_ps.wx_pc_combine(
                country_code=self.params.country_code,
                mobile=self.params.mobile,
                unionid=self.current_user.sysuser.unionid
            )

            if response.status != const.API_SUCCESS:
                return

            ret_user_id = response.data.id

            # 神策数据关联：用户注册后将匿名ID与user_id绑定
            self.sa.track_signup(ret_user_id, self.current_user.sysuser.id)
            self.logger.debug("[sensors_signup_mobile]ret_user_id: {}, origin_user_id: {}".format(ret_user_id, self.current_user.sysuser.id))

            if self.is_platform:
                source = const.WECHAT_REGISTER_SOURCE_PLATFORM
            else:
                source = const.WECHAT_REGISTER_SOURCE_QX

            self.track('cUserReg', properties={'origin': source}, distinct_id=ret_user_id, is_login_id=True)
            self.profile_set(profiles={'mobile_register_time': curr_now()}, distinct_id=ret_user_id, is_login_id=True, once=True)

            if str(ret_user_id) != str(self.current_user.sysuser.id):
                self.logger.warn("触发帐号合并成功 合并前 user_id:{} 合并后 user_id:{}".format(self.current_user.sysuser.id, ret_user_id))
                # 由于在 baseHandler 中已经有对合并帐号的处理，此处不手动删除 cookie
                # self.clear_cookie(name=const.COOKIE_SESSIONID)

        else:
            password = self.current_user.sysuser.password
            if not password:
                # 生成随机密码
                code, password = password_crypt()
                # 发送注册成功短信
                params = ObjectDict({
                    "mobile": self.params.mobile,
                    "code": code,
                })
                yield self.cellphone_ps.send_sms(
                    SmsType.UPDATE_SYSUSER_SMS, self.params.mobile,
                    params, isqx=self.is_qx,
                    ip=self.request.headers.get('Remoteip'))

            yield self.user_ps.bind_mobile_password(
                self.current_user.sysuser.id, self.params.mobile, password)



    @gen.coroutine
    def _opt_post_user_account_change(self):

        # 调用基础服务换修改手机号
        response = yield self.cellphone_ps.wx_change_mobile(
            country_code=self.params.country_code,
            mobile=self.params.mobile,
            user_id=self.current_user.sysuser.id
        )

        if response.status != const.API_SUCCESS:
            return

        ret_user_id = response.data.id
        if str(ret_user_id) != str(self.current_user.sysuser.id):
            self.logger.warn("触发帐号合并成功 合并前 user_id:{} 合并后 user_id:{}".format(self.current_user.sysuser.id, ret_user_id))
            # 由于在 baseHandler 中已经有对合并帐号的处理，此处不手动删除 cookie
            # self.clear_cookie(name=const.COOKIE_SESSIONID)
