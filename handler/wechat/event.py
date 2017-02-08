# coding=utf-8

# @Time    : 2/6/17 09:03
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     : 微信消息，指仟寻服务器与微信服务器之间的消息交互

# Copyright 2016 MoSeeker

import hashlib
from tornado import gen

from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.xml_tool import parse_msg
from util.wechat.msgcrypt import WXBizMsgCrypt


class WechatOauthHandler(MetaBaseHandler):

    """开发者模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatOauthHandler, self).__init__(application, request, **kwargs)

        self.component_app_id = self.settings.component_app_id
        self.component_encodingAESKey = self.settings.component_encodingAESKey
        self.component_token = self.settings.component_token
        # 0:开发者模式 1:第三方授权模式
        self.third_oauth = 0
        self.msg = None
        self.wechat = None

    def check_xsrf_cookie(self):
        return True

    @gen.coroutine
    def prepare(self):
        wechat_id = self.params.id
        wechat = yield self.event_ps.get_wechat(params={
            "id": wechat_id,
            "third_oauth": self.third_oauth
        })
        self.wechat = wechat
        self.msg = self.get_msg()
        yield self._get_current_user(wechat)

    @gen.coroutine
    def _get_current_user(self):
        user = ObjectDict()

        openid = self.msg.get('FromUserName', '')
        wxuser = yield self.event_ps.get_wxuser_by_openid(openid, self.wechat.id)

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
        self.logger.debug("oauth current_user: %s" % self.current_user)

        try:
            msg_type = self.msg['MsgType']
            if self.verification():
                yield getattr(self, 'post_' + msg_type)()
            else:
                self.logger.error("[wechat_oauth]verification failed:{}".format(self.msg))
        except Exception as e:
            self.logger.error(e)


    @handle_response
    @gen.coroutine
    def post_event(self):
        """微信事件, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140454&t=0.6181039380535693"""
        event = self.msg['Event']
        yield getattr(self, 'event_' + event)()

    @handle_response
    @gen.coroutine
    def post_verify(self):
        pass

    @handle_response
    @gen.coroutine
    def post_text(self):
        """文本消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
        self.logger.debug("post_text")
        pass

    # @handle_response
    # @gen.coroutine
    # def post_image(self):
    #     """图片消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
    #     self.write(self.rep_default(msg))
    #
    # @handle_response
    # @gen.coroutine
    # def post_voice(self, msg):
    #     """语音消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
    #     self.write(self.rep_default(msg))
    #
    # @handle_response
    # @gen.coroutine
    # def post_video(self, msg):
    #     """视频消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
    #     self.write(self.rep_default(msg))
    #
    # @handle_response
    # @gen.coroutine
    # def post_shortvideo(self, msg):
    #     """小视屏消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
    #     self.write(self.rep_default(msg))
    #
    # @handle_response
    # @gen.coroutine
    # def post_location(self, msg):
    #     """地理位置消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
    #     self.write(self.rep_default(msg))
    #
    # @handle_response
    # @gen.coroutine
    # def post_link(self, msg):
    #     """链接消息, referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140453&t=0.33078310940365907"""
    #     self.write(self.rep_default(msg))


    def get_msg(self):
        from_xml = self.request.body
        self.logger.debug("base get_msg: %s" % from_xml)

        return parse_msg(from_xml)

    def verification(self):
        signature = self.params.signature
        timestamp = self.params.timestamp
        nonce = self.params.nonce

        tmplist = [self.wechat.token, timestamp, nonce] if self.wechat.token else []
        tmplist.sort()
        tmpstr = ''.join(tmplist)
        hashstr = hashlib.sha1(tmpstr).hexdigest()

        if hashstr == signature:
            return True
        return False



class WechatThirdOauthHandler(WechatOauthHandler):

    """第三方授权模式"""

    def __init__(self, application, request, **kwargs):
        super(WechatThirdOauthHandler, self).__init__(application, request, **kwargs)

        self.third_oauth = 1
        self.msg = None
        self.wechat = None

    def verification(self):
        return True

    @gen.coroutine
    def prepare(self):
        pass

    @handle_response
    @gen.coroutine
    def post(self, app_id):

        if app_id:
            wechat = yield self.event_ps.get_wechat(params={
                "appid": app_id,
                "third_oauth": self.third_oauth
            })

            self.wechat = wechat
            self.msg = self.get_msg()
            if wechat:
                yield self._get_current_user()
                yield self._post()
            else:
                # TODO 返回的默认消息
                pass

        else:
            # TODO 返回的默认消息
            pass

    def get_msg(self):

        from_xml = self.request.body
        timestamp = self.params.timestamp
        msg_sign = self.params.msg_signature
        nonce = self.params.nonce

        self.logger.debug("requests: %s" % self.request)
        self.logger.debug("from_xml: %s" % from_xml)
        self.logger.debug("timestamp: %s" % timestamp)
        self.logger.debug("msg_sign: %s" % msg_sign)
        self.logger.debug("nonce: %s" %  nonce)

        from_xml = """<xml>
        <ToUserName><![CDATA[gh_04300a34b7fa]]></ToUserName>
        <Encrypt><![CDATA[db47zq/5zM6GH2rTbEP9QT7J97/ygB/HV81bqC30qEie1Ykw+lweA5k0e4u0uyG9GgkcOK+kZMB45XiLgLjJTyCczHYfmdzDANRUGs7cVNKGM1MCUaOgSTqAWWnNjHOA++wYiqmq6jbgby3KdGScN24+yLokZ46mH0lo0OyivsR944FMK7fafWAtokANlXH23PW0/u21t55/VjcD71qyKhQim1pFKqknIvUxd1glCnJ505iGVQrXCbFM9Bl62n2fkFaX8v4/5yLT8BxDR11HT9YbqPBtk00DMGW5N4ftNtaxMj99ELCfJOKA69Fo+2godjBvGKdVmiJhAE4W5lq0bSIj4v5TDE+7SdVK9Qmt6dQxNQi0on+MVteyFxEwn3a717XohPxyDCJCdCFEtTl9DB9sOgyvPy8jVM/Cj3t7yrk=]]></Encrypt>
        </xml>"""
        timestamp = '1486541176'
        msg_sign='ca1f51583463f5ee9d1e0213dcee4484d70aab21'
        nonce='1542922659'

        try:
            decrypt = WXBizMsgCrypt(self.component_token, self.component_encodingAESKey, self.component_app_id)
            ret, decryp_xml = decrypt.DecryptMsg(from_xml, msg_sign, timestamp, nonce)
        except Exception as e:
            self.LOG.error(e)

        from_xml = decryp_xml

        self.logger.debug("third get_msg: %s" % from_xml)
        return parse_msg(from_xml)
