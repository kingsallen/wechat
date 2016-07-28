# coding=utf-8

from handler.base import BaseHandler

import hashlib
from tornado import gen
from utils.common.decorator import handle_response_error


class WechatHandler(BaseHandler):

    @handle_response_error
    @gen.coroutine
    def get(self):

        self.send_json({
                "msg": self.constant.RESPONSE_SUCCESS,
                "data": {
                    "a": 'hello world!'
                }
            })

    # def get(self, *args, **kwargs):
    #     """
    #     公众平台接入
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     self.write("hello")
    #     # if self.get_argument("echostr", "") and self._verify_wexin_request():
    #     #     ret = self.get_argument("echostr", "", True)
    #     #     self.write(ret)
    #
    # def _verify_wexin_request(self):
    #     signature = self.get_argument("signature")
    #     timestamp = self.get_argument("timestamp")
    #     nonce = self.get_argument("nonce")
    #     # id = self.get_argument("id")
    #     #
    #     # token = self.db.get(
    #     #     "SELECT token FROM hr_wx_wechat "
    #     #     "WHERE id = %s", id)
    #     token = "cd717d02a93d11e5a2be00163e004a1f"
    #
    #     hashstr = hashlib.sha1(
    #         "".join(sorted([token, timestamp, nonce]))).hexdigest()
    #
    #     return hashstr == signature
