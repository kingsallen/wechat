# coding=utf-8

from tornado import gen

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

        result, data = yield self.privacy_ps.if_agree_privacy(user_id, status)

        if result:
            self.send_json_success()
        else:
            self.send_json_error()
