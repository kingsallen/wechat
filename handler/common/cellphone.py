# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.13

"""
from tornado import gen

import conf.common as const
import conf.message as msg

from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.common.cipher import encode_id


class CellphoneBindHandler(BaseHandler):
    """ 发送短信验证码的共通方法
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    @handle_response
    @gen.coroutine
    def get(self):
        result = yield self.cellphone_ps.send_valid_code(
            self.params.get('mobile', None),
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
        else:
            self.send_json_success()

    @handle_response
    @gen.coroutine
    def post(self):
        """校验短信验证码
        必要时合并账号并清空 cookie
        """
        try:
            self.guarantee('mobile', 'code')
        except:
            return

        # 验证验证码
        response = yield self.cellphone_ps.verify_mobile(
            params=self.params,
        )
        if response.status != const.API_SUCCESS:
            self.send_json_error(message=response.message)
            return
        elif response.data == const.NO:
            self.send_json_error(message=msg.CELLPHONE_INVALID_CODE)
            return

        # 检查是否需要合并 pc 账号
        response = yield self.cellphone_ps.wx_pc_combine(
            mobile=self.params.mobile,
            unionid=self.current_user.sysuser.unionid,
        )
        if response.status != const.API_SUCCESS:
            self.send_json_error(message=response.message)
            return

        ret_user_id = response.data.id
        if str(ret_user_id) != str(self.current_user.sysuser.id):
            self.clear_cookie(name=const.COOKIE_SESSIONID)

        else:
            yield self.user_ps.bind_mobile(self.current_user.sysuser.id,
                                           self.params.mobile)

        # 返回加密的 code 值，供前端拼接 url，以验证用户重要操作是否已经验证手机号
        self.send_json_success(data={
            "mc": encode_id(self.params.code, 12)
        })

        self.set_secure_cookie(const.COOKIE_MOBILE_CODE, self.params.code, expires_days=0.01, httponly=True, )
