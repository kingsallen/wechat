# coding=utf-8

from handler.base import BaseHandler

import conf.common as const
from tornado import gen
from util.common.decorator import handle_response, authenticated


class UserMobileBindedHandler(BaseHandler):

    """是否绑定了手机号"""
    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        res = str(self.current_user.sysuser.mobile) == self.current_user.sysuser.username

        if res:
            self.send_json_success(data=const.YES)
        else:
            self.send_json_success(data=const.NO)
