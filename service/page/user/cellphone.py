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
import conf.message as mes_const


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
                response = yield http_post(route, req)
            except Exception as error:
                self.logger.warn(error)
                raise gen.Return(ObjectDict({
                    'status': 1, 'message': mes_const.BASIC_SERVER_BUSY}))
            raise gen.Return(ObjectDict(response))
        else:
            raise gen.Return(ObjectDict({
                'status': 1, 'message': mes_const.REQUEST_PARAM_ERROR}))

    @gen.coroutine
    def bind_mobile(self, data, app_id):
        route = 'user/verifyCode'

        req = ObjectDict({
            'mobile': data.mobile,
            'code': data.code,
            'type': 4,
            'appid': app_id
        })
        try:
            response = yield http_post(route, req)
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(ObjectDict({
                'status': 1,
                'message': mes_const.BASIC_SERVER_BUSY
            }))
        raise gen.Return(response)
