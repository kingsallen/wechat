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
    def opt_default(self, msg, wechat):
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
            yield getattr(self, 'rep_{}'.format(rule.module))(msg, rule.id, wechat)
        else:
            raise gen.Return("")

    @gen.coroutine
    def rep_basic(self, msg, rule_id, wechat=None):
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
        yield self.wx_rep_text(msg, reply, wechat)

    @gen.coroutine
    def rep_image(self, msg, rule_id, wechat=None):
        """hr_wx_rule 中 module为 image 的处理。暂不支持
        :param msg:
        :param rule_id: hr_wx_rule.id
        :return:
        """
        raise gen.Return("")

    @gen.coroutine
    def rep_news(self, msg, rule_id, wechat=None):
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
            encryp_test = WXBizMsgCrypt(self.component_token, self.component_encodingAESKey, self.component_app_id)
            ret, encrypt_xml = encryp_test.EncryptMsg(news_info, self.params.nonce)

            news_info = encrypt_xml

        raise gen.Return(news_info)


    @gen.coroutine
    def opt_follow(self, wechat, msg):
        """处理用户关注微信后的欢迎语
        :param msg:
        :return:
        """
        rule = yield self.hr_wx_rule_ds.get_wx_rule(conds={
            "wechat_id": wechat.id,
            "id": wechat.welcome,
        })

        if rule:
            yield getattr(self, 'wx_rep_{}'.format(rule.module))(wechat, msg, rule.id)
        else:
            raise gen.Return("")

    @gen.coroutine
    def wx_rep_text(self, msg, text, wechat):
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
            # 第三方授权方式
            encryp_test = WXBizMsgCrypt(self.component_token, self.component_encodingAESKey, self.component_app_id)
            ret, encrypt_xml = encryp_test.EncryptMsg(text_info, self.params.nonce)

            text_info = encrypt_xml

        raise gen.Return(text_info)
