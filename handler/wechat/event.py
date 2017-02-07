# coding=utf-8

# @Time    : 2/6/17 09:03
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     : 微信消息，指仟寻服务器与微信服务器之间的消息交互

# Copyright 2016 MoSeeker

from tornado import gen

from handler.metabase import MetaBaseHandler
from util.common.decorator import handle_response


class WechatOauthHandler(MetaBaseHandler):

    """开发者模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatOauthHandler, self).__init__(application, request, **kwargs)

        self.third_oauth = 0
        self.component_app_id = self.settings.component_app_id
        self.component_encodingAESKey = self.settings.component_encodingAESKey
        self.component_token = self.settings.component_token

    def check_xsrf_cookie(self):
        return True

    def _verification(self):
        return True

    @gen.coroutine
    def prepare(self):


        wechat_id = self.params.id

    @gen.coroutine
    def _get_current_user(self, wechat_id):
        pass

    @handle_response
    @gen.coroutine
    def get(self):
        self.logger.debug("wechat oauth: %s" % self.request.uri)



class WechatThirdOauthHandler(WechatOauthHandler):

    """第三方授权模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatThirdOauthHandler, self).__init__(application, request, **kwargs)

        self.third_oauth = 1

    def _verification(self):
        return True

    @handle_response
    @gen.coroutine
    def post(self, app_id):
        pass

    @handle_response
    @gen.coroutine
    def get(self, appid):
        self.logger.debug("wechat thirdoauth appid: %s" % appid)
        self.logger.debug("wechat thirdoauth: %s" % self.request.uri)





