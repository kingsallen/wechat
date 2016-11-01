# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.13

"""

import conf.common as const

from tornado import gen
from handler.base import BaseHandler
import conf.message as msg


class CellphoneBindHandler(BaseHandler):
    """ 发送短信验证码的共通方法
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    @gen.coroutine
    def get(self):
        result = yield self.cellphone_ps.send_valid_code(
            self.params.get('mobile', None),
            self.app_id
        )
        if result.status != const.API_SUCCESS:
            self.send_json_error(message=result.message)
        else:
            self.send_json_success()

    @gen.coroutine
    def post(self):
        """校验短信验证码
        必要时合并账号并清空 cookie
        """
        try:
            self.guarantee('mobile', 'code')
        except:
            return

        response = yield self.cellphone_ps.bind_mobile(
            params=self.params,
            app_id=self.app_id,
            sysuser_id=self.current_user.sysuser.id
        )

        if response.status != const.API_SUCCESS:
            self.send_json_error(message=response.message)
            return

        new_user_id = self.cellphone_ps.wx_pc_combine(
            mobile=self.params.mobile,
            unionid=self.current_user.sysuser.unionid,
            app_id=self.app_id
        )

        if new_user_id and new_user_id != self.current_user.sysuser.id:
            self.clear_cookie(name=const.COOKIE_SESSIONID)
        elif new_user_id is None:
            self.send_json_error()
            return

        self.send_json_success()
