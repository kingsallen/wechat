# coding=utf-8

# @Time    : 2/7/17 15:38
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     :

# Copyright 2016 MoSeeker

import time
from tornado import gen

import conf.common as const
import conf.wechat as wx_const
from service.page.base import PageService
from util.wechat.msgcrypt import WXBizMsgCrypt
from util.tool.url_tool import make_static_url


class EventPageService(PageService):

    @gen.coroutine
    def opt_default(self, msg, nonce, wechat):
        """被动回复用户消息的总控处理
        referer: https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140543&t=0.5116553557196903
        :param msg: 消息
        :param nonce:
        :param wechat:
        :return:
        """

        rule = yield self.hr_wx_rule_ds.get_wx_rule(conds={
            "wechat_id": wechat.id,
            "id": wechat.default,
        })

        if rule:
            res = yield getattr(self, 'rep_{}'.format(rule.module))(msg, rule.id, nonce, wechat)
            raise gen.Return(res)
        else:
            raise gen.Return("")

    @gen.coroutine
    def rep_basic(self, msg, rule_id, nonce=None, wechat=None):
        """hr_wx_rule 中 module为 basic 的文字处理
        :param msg: 消息
        :param rule_id: hr_wx_rule.id
        :param nonce:
        :param wechat:
        :return:
        """

        if rule_id is None:
            raise gen.Return("")

        reply = yield self.hr_wx_basic_reply_ds.get_wx_basic_reply(conds={
            "rid": rule_id
        })
        res = yield self.wx_rep_text(msg, reply.content, wechat, nonce)
        raise gen.Return(res)

    @gen.coroutine
    def rep_image(self, msg, rule_id, nonce=None, wechat=None):
        """hr_wx_rule 中 module为 image 的处理。暂不支持
        :param msg:
        :param rule_id: hr_wx_rule.id
        :param nonce:
        :param wechat:
        :return:
        """
        raise gen.Return("")

    @gen.coroutine
    def rep_news(self, msg, rule_id, nonce, wechat=None):
        """hr_wx_rule 中 module为 news 的图文处理
        :param msg:
        :param rule_id: hr_wx_rule.id
        :param nonce:
        :param wechat:
        :return:
        """

        replies = yield self.hr_wx_news_reply_ds.get_wx_news_replys(conds={
            "rid": rule_id
        }, appends=[
            "ORDER BY parentid, id"
        ])

        news = wx_const.WX_NEWS_REPLY_HEAD_TPL % (msg.FromUserName,
                                         msg.ToUserName,
                                         str(time.time()),
                                         len(replies))

        for replie in replies:
            item = wx_const.WX_NEWS_REPLY_ITEM_TPL % (
                replie.title,
                replie.description,
                make_static_url(replie.thumb),
                replie.url
            )
            news += item

        news_info = news + wx_const.WX_NEWS_REPLY_FOOT_TPL

        if wechat.third_oauth == 1:
            # 第三方授权方式
            news_info = self._encryMsg(news_info, nonce)

        raise gen.Return(news_info)

    @gen.coroutine
    def opt_text(self, msg, nonce, wechat):
        """针对用户的文本消息，被动回复消息
        :param msg: 消息
        :param nonce:
        :param wechat:
        :return:
        """

        keyword = msg.Content.strip()
        keyword_head = keyword.split(' ')[0]

        rules = yield self.hr_wx_rule_ds.get_wx_rules(conds={
            "wechat_id": wechat.id,
            "status": const.OLD_YES,
        })

        rule = None
        for rule in rules:
            if rule.keywords and keyword_head in str(rule.keywords).replace("，", ",").split(","):
                break
            else:
                rule = None

        if rule:
            res = yield getattr(self, 'rep_{}'.format(rule.module))(msg, rule.id, nonce, wechat)
            raise gen.Return(res)
        else:
            res = yield self.opt_default(msg, nonce, wechat)
            raise gen.Return(res)


    @gen.coroutine
    def opt_follow(self, msg, wechat, nonce):
        """处理用户关注微信后的欢迎语
        :param msg:
        :param nonce:
        :param wechat:
        :return:
        """
        rule = yield self.hr_wx_rule_ds.get_wx_rule(conds={
            "wechat_id": wechat.id,
            "id": wechat.welcome,
        })

        if rule:
            res = yield getattr(self, 'wx_rep_{}'.format(rule.module))(msg, rule, wechat, nonce)
            raise gen.Return(res)
        else:
            raise gen.Return("")

    @gen.coroutine
    def wx_rep_text(self, msg, text, wechat, nonce):
        """微信交互：回复文本消息
        :param msg: 消息
        :param text: 文本消息
        :param nonce:
        :param wechat:
        :return:
        """

        if text is None:
            raise gen.Return("")

        text = "hello"

        text_info = wx_const.WX_TEXT_REPLY % (msg.FromUserName,
                                            msg.ToUserName,
                                            int(time.time()),
                                            text)

        if wechat.third_oauth == 1:
            text_info = self._encryMsg(text_info, nonce)

        self.logger.debug("text_info: %s" % text_info)

        raise gen.Return(text_info)

    def _encryMsg(self, uncrypt_xml, nonce):
        """
        第三方授权方式返回的 xml 需要加密
        :param uncrypt_xml:
        :param nonce:
        :return:
        """

        decrypt_obj = WXBizMsgCrypt(self.settings.component_app_id,
                                    self.settings.component_encodingAESKey,
                                    self.settings.component_token)

        ret, encrypt_xml = decrypt_obj.EncryptMsg(uncrypt_xml, nonce)

        print ("+++++++++")
        print (uncrypt_xml)
        print (nonce)
        print (encrypt_xml)
        print("+++++++++")

        return encrypt_xml
