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
        是否同意弹出的"隐私协议": 用户如果点击同意，删除user_privacy_record表相关记录，如果拒绝，不删除
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
    用户是否同意过隐私协议 [用于决定是否需要弹出隐私协议]
    """

    @handle_response
    @gen.coroutine
    def get(self):
        """
        用户是否同意过隐私协议：data=0表示同意过，1表示没同意过。user_privacy_record有记录表示拒绝，没有记录表示同意过
        -path: /api/privacy/is_agree/
        :return: {
            "status": 0,
            "message": "success",
            "data": 1
        }

        新用户：只有特定页面打开新协议
        老用户已经同意老协议：打开任何网页都弹出新协议，如果拒绝，特殊页面需要弹层同意才能访问，其它页面可以继续访问，24小时之后进任意界面还需要弹层
        老用户拒绝老协议：跟新用户一致【只有同意过新协议的用户返回true】
        注意：第一、三种用户跟以前一致，只有第二种情况需要再分情况：user_privacy_record没有记录【已经同意老协议】，如果已经同意新协议无需再弹层，如果拒绝新协议，不同页面需要做不同处理
        """
        user_id = self.current_user.sysuser.id
        result, show_privacy_agreement = yield self.privacy_ps.if_privacy_agreement_window(user_id)

        if result:
            self.send_json_success(data=not show_privacy_agreement)
        else:
            self.send_json_error()
