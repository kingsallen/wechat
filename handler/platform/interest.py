# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.20

"""

from tornado import gen
from handler.base import BaseHandler


class InterestHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        # Debug temperary param
        # sysuser = yield self.user_ps.get_user_user_id(393881)
        sysuser = yield self.user_ps.get_user_user_id(
                    self.current_user.sysuser.id)
        if sysuser and str(sysuser.mobile) == sysuser.username:
            status_code, message = 'o', 'User already binds mobile'
        else:
            status_code, message = 'x', 'User does not bind mobile'

        self.send_json(data=None, status_code=status_code, message=message)
        return

    @gen.coroutine
    def post(self):

        response = yield self.user_ps.update_user_user(
            sysuser_id=self.current_user.sysuser.id,
            # sysuser_id=393888,
            data=self.json_args
        )
        print('response--{}'.format(response))
        self.send_json(data=None, status_code=response.status,
                       message=response.message)
        return
