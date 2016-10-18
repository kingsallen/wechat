# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.17

"""

from tornado import gen
from util.common import ObjectDict
from service.page.base import PageService
from util.tool.http_tool import http_post


class CellphonePageService(PageService):
    """
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    @gen.coroutine
    def send_valid_code(self, mobile_numb, app_id):
        route = 'user/sendCode'
        if mobile_numb:
            req = ObjectDict({
                'mobile': mobile_numb,
                'type': 4,
                'appid': app_id
            })
            try:
                response = yield http_post(route, req, infra=True)
                raise gen.Return(response)
            except Exception as error:
                self.logger(error)
                raise gen.Return({'status': 1,
                                  'message': 'Basic service server busy.'})
        else:
            raise gen.Return({'status': 1,
                              'message': 'Request with wrong param'})

    @gen.coroutine
    def bind_mobile(self, json_args, app_id):
        route = 'user/verifyCode'
        if json_args and 'mobile' in json_args.keys() and \
                'code' in json_args.keys():
            req = ObjectDict({
                'mobile': json_args.get('mobile'),
                'code': json_args.get('code'),
                'type': 4,
                'appid': app_id
            })
            try:
                response = yield http_post(route, req, infra=True)
                raise gen.Return(response)
            except Exception as error:
                self.logger(error)
                raise gen.Return({'status': 1,
                                  'message': 'Basic service server busy.'})
        else:
            raise gen.Return({'status': 1,
                              'message': 'Request with wrong param.'})
