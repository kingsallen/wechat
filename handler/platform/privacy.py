# coding=utf-8

from tornado import gen

import conf.common as const

from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated


class PrivacyHandler(BaseHandler):
    """
    隐私协议
    """

    @handle_response
    @gen.coroutine
    def post(self):
        """
        是否同意弹出的"隐私协议"
        -path: /api/privacy/agree
        -params:
        {
            "agree": 1, // 1: 同意， 0: 不同意
        }
        :return: {
            "status": 0,
            "message": "success"
        }

        """
        user_id = self.current_user.sysuser.id
        status = self.json_args.get('agree')

        result = yield self.privacy_ps.if_agree_privacy(user_id, status)

        if result.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error(message=result.message)


class IsAgreePrivacyHandler(BaseHandler):
    """
    用户是否同意过隐私协议
    """

    @handle_response
    @gen.coroutine
    def get(self):
        """
        用户是否同意过隐私协议：data=0表示同意过，1表示没同意过
        -path: /api/privacy/is_agree/
        :return: {
            "status": 0,
            "message": "success",
            "data": 1
        }

        """
        user_id = self.current_user.sysuser.id
        result, show_privacy_agreement = yield self.privacy_ps.if_privacy_agreement_window(user_id)

        if result:
            self.send_json_success(data=not show_privacy_agreement)
        else:
            self.send_json_error()
