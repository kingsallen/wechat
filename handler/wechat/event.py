# coding=utf-8

# @Time    : 1/24/17 17:03
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     : 微信消息，指仟寻服务器与微信服务器之间的消息交互

# Copyright 2016 MoSeeker

# class WechatHandler(BaseHandler):
#
#     @handle_response
#     @gen.coroutine
#     def get(self):
#
#         self.send_json_success(
#                 data={
#                     "a": 'hello world!'
#                 }
#             )

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
