# coding=utf-8

# @Time    : 2/6/17 09:03
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     : 微信消息，指仟寻服务器与微信服务器之间的消息交互

# Copyright 2016 MoSeeker

import traceback
from tornado import gen

from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.xml_tool import parse_msg
from util.wechat.msgcrypt import WXBizMsgCrypt, SHA1


class WechatOauthHandler(MetaBaseHandler):

    """开发者模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatOauthHandler, self).__init__(application, request, **kwargs)

        # 0:开发者模式 1:第三方授权模式
        self.third_oauth = 0
        self.msg = None
        self.wechat = None

    def check_xsrf_cookie(self):
        return True

    @gen.coroutine
    def prepare(self):
        self.msg = self.get_msg()
        wechat_id = self.params.id
        wechat = yield self.wechat_ps.get_wechat(conds={
            "id": wechat_id,
            "third_oauth": self.third_oauth
        })

        self.wechat = wechat
        yield self._get_current_user()

    @gen.coroutine
    def _get_current_user(self):
        user = ObjectDict()

        openid = self.msg.get('FromUserName', '')
        wxuser = yield self.user_ps.get_wxuser_openid_wechat_id(openid, self.wechat.id)

        user.wechat = self.wechat
        user.wxuser = wxuser
        self.current_user = user

    @handle_response
    @gen.coroutine
    def post(self):
        yield self._post()


    @handle_response
    @gen.coroutine
    def _post(self):

        self.logger.debug("oauth: %s" % self.request.uri)
        self.logger.debug("oauth msg: %s" % self.msg)
        self.logger.debug("oauth params: %s" % self.params)
        self.logger.debug("oauth current_user: %s" % self.current_user)

        try:
            msg_type = self.msg['MsgType']
            if self.verification():
                yield getattr(self, 'post_' + msg_type)()
            else:
                self.logger.error("[wechat_oauth]verification failed:{}".format(self.msg))
        except Exception as e:
            self.logger.error(traceback.format_exc())

    @handle_response
    @gen.coroutine
    def post_verify(self):
        self.send_xml()

    @handle_response
    @gen.coroutine
    def post_text(self):
        """文本消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_text(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)


    @handle_response
    @gen.coroutine
    def post_image(self):
        """图片消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_default(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)

    @handle_response
    @gen.coroutine
    def post_voice(self):
        """语音消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_default(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)

    @handle_response
    @gen.coroutine
    def post_video(self):
        """视频消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_default(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)

    @handle_response
    @gen.coroutine
    def post_shortvideo(self):
        """小视屏消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_default(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)

    @handle_response
    @gen.coroutine
    def post_location(self):
        """地理位置消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_default(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)

    @handle_response
    @gen.coroutine
    def post_link(self):
        """链接消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        res = yield self.event_ps.opt_default(self.msg, self.params.nonce, self.wechat)
        self.send_xml(res)


    @handle_response
    @gen.coroutine
    def post_event(self):
        """微信事件, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140454&t=0.6181039380535693"""
        event = self.msg['Event']
        yield getattr(self, 'event_' + event)()





    def on_finish(self):
        """继承MetaBaseHandler.on_finish(),添加部分日志"""

        self.log_info = {"wxmsg": self.msg}
        super().on_finish()

    def get_msg(self):
        from_xml = self.request.body
        return parse_msg(from_xml)

    def verification(self):
        """
        验证 POST 数据是否真实有效
        :return:
        """
        if not self.wechat.token:
            return False

        try:
            ret, hashstr = SHA1().getSHA1(self.wechat.token,
                                          self.params.timestamp,
                                          self.params.nonce,
                                          '')
        except Exception as e:
            self.logger.error(traceback.format_exc())

        if hashstr == self.params.signature:
            return True

        return False


class WechatThirdOauthHandler(WechatOauthHandler):

    """第三方授权模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatThirdOauthHandler, self).__init__(application, request, **kwargs)

        self.component_app_id = self.settings.component_app_id
        self.component_encodingAESKey = self.settings.component_encodingAESKey
        self.component_token = self.settings.component_token

        self.third_oauth = 1
        self.msg = None
        self.wechat = None

    def verification(self):
        """第三方授权模式，暂未做消息加密验证"""
        return True

    @gen.coroutine
    def prepare(self):
        pass

    @handle_response
    @gen.coroutine
    def post(self, app_id):

        if app_id:
            self.msg = self.get_msg()
            wechat = yield self.wechat_ps.get_wechat(conds={
                "appid": app_id,
                "third_oauth": self.third_oauth
            })

            self.wechat = wechat
            if wechat:
                yield self._get_current_user()
                yield self._post()
            else:
                self.send_xml()

        else:
            self.send_xml()

    def get_msg(self):

        try:
            decrypt = WXBizMsgCrypt(self.component_token, self.component_encodingAESKey, self.component_app_id)
            ret, decryp_xml = decrypt.DecryptMsg(self.request.body,
                                                 self.params.msg_signature,
                                                 self.params.timestamp,
                                                 self.params.nonce)
        except Exception as e:
            self.LOG.error(traceback.format_exc())

        return parse_msg(decryp_xml)
