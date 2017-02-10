# coding=utf-8

# @Time    : 2/7/17 15:38
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     :

# Copyright 2016 MoSeeker

import re
import time
import traceback
from tornado import gen

import conf.common as const
import conf.wechat as wx_const
from cache.user.user_hr_account import UserHrAccountCache
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

        text_info = wx_const.WX_TEXT_REPLY % (msg.FromUserName,
                                            msg.ToUserName,
                                            int(time.time()),
                                            text)

        if wechat.third_oauth == 1:
            text_info = self._encryMsg(text_info, nonce)

        self.logger.debug("text_info: %s" % text_info)

        raise gen.Return(text_info)


    @gen.coroutine
    def opt_event_subscribe(self, msg, current_user, nonce):

        openid = msg.FromUserName

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用
        if current_user.wechat.id == self.settings.qx_wechat_id and msg.EventKey:
            if current_user.wxuser:
                # TODO
                yield self._update_wxuser()

            # 临时二维码处理逻辑, 5位type+27为自定义id
            int_scene_id = re.match(r'qrscene_(\d+)', msg.EventKey)
            if int_scene_id:
                # TODO
                yield self._do_weixin_qrcode(msg)


        if not current_user.wxuser:
            # 新微信用户
            # TODO
            wxuser = yield self._create_wxuser()

            # 关注仟寻招聘助手时，将 user_hr_account.wxuser_id 与 wxuser 绑定
            if current_user.wechat.id == self.settings.help_wechat_id and msg.EventKey:
                try:
                    hr_id = re.match(r'qrscene_([0-9]*)_([0-9]*)_([0-9]*)', msg['EventKey'])
                    # 扫码换绑
                    if hr_id.group(1) and int(hr_id.group(3)) == 1:
                        yield self.user_hr_account_ds.update_hr_account(
                            conds={
                                "id": int(hr_id.group(1))
                            }, fields={
                                "wxuser_id": int(wxuser.id)
                            })
                    # 初次绑定
                    elif hr_id.group(1):
                        yield self.user_hr_account_ds.update_hr_account(
                            conds={
                                "id": int(hr_id.group(1)),
                                "wxuser_id": ['NULL', 'is']
                            }, fields={
                                "wxuser_id": int(wxuser.id)
                            })

                    # 更新 user_hr_account 的缓存,HR招聘管理平台使用,需同时更新 wxuser_id 和 wxuser
                    user_hr_account_cache = UserHrAccountCache()
                    user_hr_account_cache.update_user_hr_account_session(
                        hr_id.group(1),
                        value={
                            "wxuser_id": int(wxuser.id),
                            "wxuser": wxuser
                        })

                    # HR招聘管理平台对于HR 帐号绑定微信长轮训机制，需要实时的将状态返回给 HR 平台
                    user_hr_account_cache.pub_wx_binding(hr_id.group(1))
                except Exception as e:
                    self.logger.error("[wechat][opt_event_subscribe]binding user_hr_account "
                                      "failed: {}".format(traceback.format_exc()))
                    user_hr_account_cache.pub_wx_binding(hr_id.group(1), msg='-1')
        else:
            # 老微信用户
            # TODO
            yield self._update_wxuser()

        res = self.opt_follow(msg, current_user.wechat, nonce)
        raise gen.Return(res)

    @gen.coroutine
    def _create_wxuser(self):
        pass

    @gen.coroutine
    def _update_wxuser(self):
        pass


    def _encryMsg(self, uncrypt_xml, nonce):
        """
        第三方授权方式返回的 xml 需要加密
        :param uncrypt_xml:
        :param nonce:
        :return:
        """

        decrypt_obj = WXBizMsgCrypt(self.settings.component_token,
                                    self.settings.component_encodingAESKey,
                                    self.settings.component_app_id)

        ret, encrypt_xml = decrypt_obj.EncryptMsg(uncrypt_xml, nonce)

        return encrypt_xml
