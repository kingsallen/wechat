# coding=utf-8

# @Time    : 2/6/17 09:03
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     : 微信消息，指仟寻服务器与微信服务器之间的消息交互

# Copyright 2016 MoSeeker

from tornado import gen

from handler.metabase import MetaBaseHandler
from util.common.decorator import handle_response
from util.tool.xml_tool import parse_msg


class WechatOauthHandler(MetaBaseHandler):

    """开发者模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatOauthHandler, self).__init__(application, request, **kwargs)

        self.component_app_id = self.settings.component_app_id
        self.component_encodingAESKey = self.settings.component_encodingAESKey
        self.component_token = self.settings.component_token
        # 0:开发者模式 1:第三方授权模式
        self.third_oauth = 0
        self.wechat_id = 0

        print (4)

    def check_xsrf_cookie(self):
        return True

    def _verification(self):
        return True

    @gen.coroutine
    def prepare(self):
        print (5)

        wechat_id = self.params.id

    @gen.coroutine
    def _get_current_user(self, wechat_id):
        pass

    @handle_response
    @gen.coroutine
    def get(self):
        print (6)
        self.logger.debug("wechat oauth: %s" % self.request.uri)


    def get_msg(self):
        from_xml = self.request.body
        return parse_msg(from_xml)



class WechatThirdOauthHandler(WechatOauthHandler):

    """第三方授权模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatThirdOauthHandler, self).__init__(application, request, **kwargs)

        self.third_oauth = 1
        self.wechat_id = 0

        print (1)

    def _verification(self):
        return True

    @handle_response
    @gen.coroutine
    def post(self, app_id):
        if app_id:
            wechat = yield self.event_ps.get_wechat(params={
                "appid": app_id,
                "third_oauth": self.third_oauth
            })

            if wechat:
                self.current_user = self._get_current_user(wechat.id)
            else:
                # TODO 返回的默认消息
                pass



        else:
            # TODO 返回的默认消息
            pass

    def get_msg(self):

        timestamp = self.params.timestamp
        msg_sign = self.params.msg_signature
        nonce = self.params.nonce
        #
        # try:
        #     decrypt_test = WXBizMsgCrypt(self.component_token, self.component_encodingAESKey, self.component_app_id)
        #     ret, decryp_xml = decrypt_test.DecryptMsg(from_xml, msg_sign, timestamp, nonce)
        #
        #     self.LOG.error("get_msg from :{0} decryp_xml: {1}".format(fr, decryp_xml))
        #     self.LOG.error("get_msg ret: %s" % ret)
        #
        # except Exception, e:
        #     self.LOG.error(e)
        #
        # from_xml = decryp_xml


        from_xml = self.request.body
        return parse_msg(from_xml)





