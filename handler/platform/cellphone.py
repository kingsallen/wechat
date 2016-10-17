# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.13

"""

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
        self.send_json(response)

        return

    @gen.coroutine
    def post(self):

        response = yield self.cellphone_ps.bind_mobile(
            json_args=self.json_args,
            app_id=self.app_id
        )
        self.send_json(response)

        return
