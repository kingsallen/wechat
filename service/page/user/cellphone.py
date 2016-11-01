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
import conf.message as msg


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
    def send_valid_code(self, mobile_numb, app_id):
        """
        Request basic service send valid code to target mobile
        :param mobile_numb: target mobile number
        :param app_id: request source(platform, qx...)
        :return:
        """
        if mobile_numb:
            req = ObjectDict({
                'mobile': mobile_numb,
                'type':   self._OPT_TYPE.change_mobile,
                'appid':  app_id
            })
            try:
                response = yield http_post(self._ROUTE.valid, req)
            except Exception as error:
                self.logger.warn(error)
                raise gen.Return(False)
            result = True if int(response.status) == 0 else False
            raise gen.Return(result)
        else:
            raise gen.Return(False)

    @gen.coroutine
    def bind_mobile(self, params, app_id, sysuser_id):
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
        try:
            response = yield http_post(self._ROUTE.verify, req)
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(ObjectDict({
                'status':  msg.FAILURE,
                'message': msg.BASIC_SERVER_BUSY
            }))

        if int(response.status) == msg.SUCCESS:
            result = yield self.user_user_ds.update_user(
                conds={
                    'id': sysuser_id
                },
                fields={
                    'mobile':   int(params.mobile),
                    'username': params.mobile
                })
            response.status, response.message = result.status, result.message

        raise gen.Return(response)

    @gen.coroutine
    def wx_pc_combine(self, mobile, unionid, app_id):
        req = ObjectDict({
            'mobile':  mobile,
            'unionid': unionid,
            'appid':   app_id
        })
        try:
            result = yield http_post(self._ROUTE.combine, req)
            self.logger.debug('Combine wx and pc uer as: {}'.format(result))
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(None)
        else:
            user_id = int(result) if result.isdigit() else msg.FAILURE
            raise gen.Return(int(user_id))
