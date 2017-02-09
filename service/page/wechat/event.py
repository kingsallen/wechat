# coding=utf-8

# @Time    : 2/7/17 15:38
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     :

# Copyright 2016 MoSeeker

import time
from tornado import gen


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
        :return:
        """

        rule = yield self.hr_wx_rule_ds.get_wx_rule(conds={
            "wechat_id": wechat.id,
            "id": wechat.default,
        })

        if rule:
            yield getattr(self, 'rep_{}'.format(rule.module))(msg, rule.id, nonce, wechat)
        else:
            raise gen.Return("")

    @gen.coroutine
    def rep_basic(self, msg, rule_id, nonce=None, wechat=None):
        """hr_wx_rule 中 module为 basic 的文字处理
        :param msg: 消息
        :param rule_id: hr_wx_rule.id
        :return:
        """

        if rule_id is None:
            raise gen.Return("")

        reply = yield self.hr_wx_basic_reply_ds.get_wx_basic_reply(conds={
            "rid": rule_id
        })
        yield self.wx_rep_text(msg, reply, wechat, nonce)

    @gen.coroutine
    def rep_image(self, msg, rule_id, nonce=None, wechat=None):
        """hr_wx_rule 中 module为 image 的处理。暂不支持
        :param msg:
        :param rule_id: hr_wx_rule.id
        :return:
        """
        raise gen.Return("")

    @gen.coroutine
    def rep_news(self, msg, rule_id, nonce, wechat=None):
        """hr_wx_rule 中 module为 news 的图文处理
        :param msg:
        :param rule_id: hr_wx_rule.id
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

        for new in news:
            item = wx_const.WX_NEWS_REPLY_ITEM_TPL % (
                new.title,
                new.description,
                make_static_url(new.thumb),
                new.url
            )
            news += item

        news_info = new + wx_const.WX_NEWS_REPLY_FOOT_TPL

        if wechat.third_oauth == 1:
            # 第三方授权方式
            news_info = self._encryMsg(news_info, nonce)

        raise gen.Return(news_info)


    @gen.coroutine
    def opt_follow(self, msg, wechat, nonce):
        """处理用户关注微信后的欢迎语
        :param msg:
        :return:
        """
        rule = yield self.hr_wx_rule_ds.get_wx_rule(conds={
            "wechat_id": wechat.id,
            "id": wechat.welcome,
        })

        if rule:
            yield getattr(self, 'wx_rep_{}'.format(rule.module))(msg, rule, wechat, nonce)
        else:
            raise gen.Return("")

    @gen.coroutine
    def wx_rep_text(self, msg, text, wechat, nonce):
        """微信交互：回复文本消息
        :param msg: 消息
        :param text: 文本消息
        :return:
        """

        text_info = wx_const.WX_TEXT_REPLY % (msg.FromUserName,
                                                   msg.ToUserName,
                                                   str(time.time()),
                                                   str(text))

        if wechat.third_oauth == 1:
            text_info = self._encryMsg(text_info, nonce)

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

        return encrypt_xml
