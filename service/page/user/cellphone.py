# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.17

"""

from tornado import gen

from service.page.base import PageService
from util.common import ObjectDict
from util.tool.http_tool import http_post


class CellphonePageService(PageService):
    """
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """
    _ROUTE = ObjectDict({
        'valid':   'user/sendCode',
        'verify':  'user/verifyCode',
        'combine': 'user/wxbindmobile'
    })

    _OPT_TYPE = ObjectDict({
        'code_login':      1,
        'forget_password': 2,
        'modify_info':     3,
        'change_mobile':   4
    })

    @gen.coroutine
    def send_valid_code(self, mobile, app_id):
        """Request basic service send valid code to target mobile
        :param mobile: target mobile number
        :param app_id: request source(platform, qx...)
        :return:
        """
        req = ObjectDict({
            'mobile': mobile,
            'type':   self._OPT_TYPE.change_mobile,
            'appid':  app_id
        })
        res = yield http_post(self._ROUTE.valid, req)
        raise gen.Return(res)

    @gen.coroutine
    def verify_mobile(self, params, app_id):
        """
        Send code submitted by user to basic service.
        :param params: dict include user mobile number and valid code
        :param app_id: request source(platform, qx...)
        :return:
        """
        req = ObjectDict({
            'mobile': params.mobile,
            'code':   params.code,
            'type':   self._OPT_TYPE.change_mobile,
            'appid':  app_id
        })

        response = yield http_post(self._ROUTE.verify, req)
        raise gen.Return(response)

    @gen.coroutine
    def wx_pc_combine(self, mobile, unionid, app_id):
        """调用账号绑定接口"""
        req = ObjectDict({
            'mobile':  mobile,
            'unionid': unionid,
            'appid':   app_id
        })

        response = yield http_post(self._ROUTE.combine, req)
        raise gen.Return(response)
