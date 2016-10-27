# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.13

"""

import conf.common as const

from tornado import gen
from handler.base import BaseHandler


class CellphoneBindHandler(BaseHandler):
    """
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    @gen.coroutine
    def get(self):

        response = yield self.cellphone_ps.send_valid_code(
            mobile_numb=self.params.get('mobile', None),
            app_id=self.app_id
        )
        self._send_json(data=None, status_code=response.status,
                       message=response.message)

        return

    @gen.coroutine
    def post(self):

        try:
            self.guarantee('mobile', 'code')
        except:
            return

        response = yield self.cellphone_ps.bind_mobile(
            params=self.params,
            app_id=self.app_id,
            sysuser_id=self.current_user.sysuser.id
        )

        if response.status != 0:
            self._send_json(data=None, status_code=response.status,
                       message=response.message)

        new_user_id = self.cellphone_ps.wx_pc_combine(
            mobile=self.params.mobile,
            unionid=self.current_user.sysuser.unionid,
            app_id=self.app_id
        )

        if new_user_id and new_user_id != self.current_user.sysuser.id:
            self.clear_cookie(name=const.SESSION_ID)
        elif new_user_id is None:
            self.send_json_error()

        self.send_json_success()

        return
