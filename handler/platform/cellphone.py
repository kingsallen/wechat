# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.13

"""

from tornado import gen
from tornado.util import ObjectDict
from handler.base import BaseHandler
from utils.tool.http_tool import http_post


class CellphoneBindHandler(BaseHandler):
    """
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    @gen.coroutine
    def get(self):
        route = 'user/sendCode'
        mobile_numb = self.params.get('mobile', None)
        if mobile_numb:
            req = ObjectDict({
                'mobile': self.params.get('mobile'),
                'type': 4,
                'appid': self.app_id
            })
            try:
                response = yield http_post(route, req, infra=True)
                self.send_json(response)
            except Exception as error:
                self.logger(error)
                self.send_json({'status': 1,
                                'message': 'Basic service server busy.'})
        else:
            self.send_json({'status': 1,
                            'message': 'Request with wrong param'})

        return

    @gen.coroutine
    def post(self):
        route = 'user/verifyCode'
        if self.json_args and 'mobile' in self.json_args.keys() and \
                'code' in self.json_args.keys():
            req = ObjectDict({
                'mobile': self.json_args.get('mobile'),
                'code': self.json_args.get('code'),
                'type': 4,
                'appid': self.app_id
            })
            try:
                response = yield http_post(route, req, infra=True)
                self.send_json(response)
            except Exception as error:
                self.logger(error)
                self.send_json({'status': 1,
                                'message': 'Basic service server busy.'})
        else:
            self.send_json({'status': 1,
                            'message': 'Request with wrong param.'})

        return
