# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.20

"""

from tornado import gen
from handler.base import BaseHandler
import conf.message as mes_const


class UserCurrentInfoHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        try:
            self.guarantee('name', 'company', 'position')
        except:
            return

        yield self.user_ps.update_user_user(
            sysuser_id=self.current_user.sysuser.id,
            data=self.params
        )

        self.send_json_success()
