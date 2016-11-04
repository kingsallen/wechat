# coding=utf-8

from handler.base import BaseHandler

import conf.common as const
from tornado import gen


class UserMobileBindedHandler(BaseHandler):
    """是否绑定了手机号"""
    @gen.coroutine
    def post(self):
        res = str(self.current_user.sysuser.mobile) == self.current_user.sysuser.username

        if res:
            self.send_json_success(data=const.YES)
        else:
            self.send_json_success(data=const.NO)
