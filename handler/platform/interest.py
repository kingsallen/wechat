# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.20

"""

from tornado import gen
from handler.base import BaseHandler
import conf.message as mes_const


class InterestHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # Debug temporary param
        # sysuser = yield self.user_ps.get_user_user_id(393881)
        sysuser = yield self.user_ps.get_user_user_id(
                    self.current_user.sysuser.id)
        if sysuser and str(sysuser.mobile) == sysuser.username:
            status_code, message = 'o', mes_const.CELLPHONE_BIND
        else:
            status_code, message = 'x', mes_const.CELLPHONE_UNBIND

        self.send_json(data=None, status_code=status_code, message=message)
        return

    @gen.coroutine
    def post(self):
        try:
            self.guarantee('name', 'company', 'position')
        except:
            return

        response = yield self.user_ps.update_user_user(
            # Debug temporary param
            # sysuser_id=393888,
            sysuser_id=self.current_user.sysuser.id,
            data=self.params
        )
        self.send_json(data=None, status_code=response.status,
                       message=response.message)
        return
