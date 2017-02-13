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
from oauth.wechat import WechatUtil
from service.page.base import PageService
from util.wechat.msgcrypt import WXBizMsgCrypt
from util.tool.url_tool import make_static_url
from util.tool.date_tool import format_time
from util.common import ObjectDict
from util.tool.json_tool import json_dumps


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
            text_info = self.__encryMsg(text_info, nonce)

        self.logger.debug("text_info: %s" % text_info)

        raise gen.Return(text_info)


    @gen.coroutine
    def opt_event_subscribe(self, msg, current_user, nonce):
        """
        处理用户关注事件
        :param msg:
        :param current_user:
        :param nonce:
        :return:
        """

        openid = msg.FromUserName
        is_newbie = False
        if not current_user.wxuser:
            # 新微信用户
            is_newbie = True
            wxuser_id = yield self._create_wxuser(openid, current_user)
            yield self.__opt_help_wxuser(wxuser_id, current_user, msg)

        else:
            # 老微信用户
            yield self._update_wxuser(openid, current_user, self.msg)

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用
        if current_user.wechat.id == self.settings.qx_wechat_id and msg.EventKey:
            # 临时二维码处理逻辑, 5位type+27为自定义id
            int_scene_id = re.match(r'qrscene_(\d+)', msg.EventKey)
            if int_scene_id:
                # TODO
                yield self._do_weixin_qrcode(msg, is_newbie=is_newbie)

        res = self.opt_follow(msg, current_user.wechat, nonce)
        raise gen.Return(res)

    @gen.coroutine
    def _create_wxuser(self, openid, current_user):
        """
        创建微信 wxuser 用户
        :param openid:
        :param current_user:
        :return:
        """
        wxuser_id = current_user.wxuser.id

        wechat_util_obj = WechatUtil()
        wechat_userinfo = yield wechat_util_obj.get_wxuser(current_user.wechat.access_token, openid)

        if not wechat_userinfo or openid is None:
            self.logger.error("[wechat_oauth][create_wxuser]wechat_userinfo is None."
                              "wechat_userinfo:{0}, openid:{1}".format(wechat_userinfo, openid))
            raise gen.Return(wxuser_id)

        # 已授权给仟寻，或者 HR 雇主平台的用户，已经创建了 wxuser，故不需要再创建 wxuser
        if (current_user.wechat.id == self.settings.help_wechat_id
            or current_user.wechat.id == self.settings.qx_wechat_id) and current_user.wxuser:
            yield self.user_wx_user_ds.update_wxuser(
                conds={"id": current_user.wxuser.id},
                fields={
                    "is_subscribe":    const.WX_USER_SUBSCRIBED,
                    "nickname":        wechat_userinfo.nickname,
                    "sex":             wechat_userinfo.sex or 0,
                    "city":            wechat_userinfo.city,
                    "country":         wechat_userinfo.country,
                    "province":        wechat_userinfo.province,
                    "language":        wechat_userinfo.language,
                    "headimgurl":      wechat_userinfo.headimgurl,
                    "unionid":         current_user.wxuser.unionid or wechat_userinfo.unionid,
                    "subscribe_time" : current_user.wxuser.subscribe_time or format_time(time.time()),
                    "source":          const.WX_USER_SOURCE_UPDATE_SHORT
                })

        if not current_user.wxuser:
            wxuser_id = yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe": const.WX_USER_SUBSCRIBED,
                "openid":         openid,
                "nickname":       wechat_userinfo.nickname,
                "sex":            wechat_userinfo.sex or 0,
                "city":           wechat_userinfo.city,
                "country":        wechat_userinfo.country,
                "province":       wechat_userinfo.province,
                "language":       wechat_userinfo.language,
                "headimgurl":     wechat_userinfo.headimgurl,
                "wechat_id":      current_user.wechat.id,
                "unionid":        wechat_userinfo.unionid or '',
                "subscribe_time": format_time(time.time()),
                "source":         const.WX_USER_SOURCE_SUBSCRIBE
            })

        raise gen.Return(wxuser_id)

    @gen.coroutine
    def _update_wxuser(self, openid, current_user, msg):
        """
        更新老微信 wxuser 信息
        :param openid:
        :param current_user:
        :param msg:
        :return:
        """

        wechat_util_obj = WechatUtil()
        wechat_userinfo = yield wechat_util_obj.get_wxuser(current_user.wechat.access_token, openid)

        if not wechat_userinfo or openid is None:
            self.logger.error("[wechat_oauth][create_wxuser]wechat_userinfo is None."
                              "wechat_userinfo:{0}, openid:{1}".format(wechat_userinfo, openid))
            raise gen.Return()

        yield self.user_wx_user_ds.update_wxuser(
            conds={"id": current_user.wxuser.id},
            fields={
                "is_subscribe": const.WX_USER_SUBSCRIBED,
                "nickname": wechat_userinfo.nickname,
                "sex": wechat_userinfo.sex or 0,
                "city": wechat_userinfo.city,
                "country": wechat_userinfo.country,
                "province": wechat_userinfo.province,
                "language": wechat_userinfo.language,
                "headimgurl": wechat_userinfo.headimgurl,
                "unionid": current_user.wxuser.unionid or wechat_userinfo.unionid,
                "subscribe_time": current_user.wxuser.subscribe_time or format_time(time.time()),
                "source": const.WX_USER_SOURCE_UPDATE_ALL
            })

        yield self.__opt_help_wxuser(current_user.wxuser.id, current_user, msg)


    @gen.coroutine
    def opt_event_unsubscribe(self, current_user):
        """
        处理用户取消关注事件
        :param msg:
        :param current_user:
        :param nonce:
        :return:
        """

        if current_user.wxuser:
            yield self.user_wx_user_ds.update_wxuser(
                conds={"id": current_user.wxuser.id},
                fields={
                    "is_subscribe": const.WX_USER_UNSUBSCRIBED,
                    "unsubscibe_time": current_user.wxuser.subscribe_time or format_time(time.time()),
                    "source": const.WX_USER_SOURCE_UNSUBSCRIBE
                })
            # 取消关注仟寻招聘助手时，将user_hr_account.wxuser_id与user_wx_user.id 解绑
            if current_user.wechat.id == self.settings.help_wechat_id:
                user_hr_account = yield self.user_hr_account_ds.get_hr_account(conds={
                    "wxuser_id": current_user.wxuser.id
                })
                if current_user:
                    yield self.user_hr_account_ds.update_hr_account(
                        conds={
                            "wxuser_id": current_user.wxuser.id
                        }, fields={
                            "wxuser_id": None
                        })
                    user_hr_account_cache = UserHrAccountCache()
                    user_hr_account_cache.update_user_hr_account_session(
                        user_hr_account.id,
                        value={
                            "wxuser_id": 0,
                            "wxuser": ObjectDict()
                        })

        raise gen.Return()

    @gen.coroutine
    def opt_event_scan(self, current_user, msg):
        """
        处理用户扫码事件
        :param current_user:
        :param msg:
        :return:
        """

        if current_user.wechat.id == self.settings.help_wechat_id and msg.EventKey:
            scan_info = re.match(r'([0-9]*)_([0-9]*)_([0-9]*)', msg.EventKey)
            # 更新仟寻招聘助手公众号下的用户openid
            yield self.user_wx_user_ds.update_wxuser(
                conds={
                    "id": scan_info.group(2),
                    "wechat_id": current_user.wechat.id,
                },
                fields={
                    "openid": msg.FromUserName,
                    "source": const.WX_USER_SOURCE_UPDATE_SHORT
                })

            # 已绑定过的微信号，不能再绑定第二个hr_account账号，否则微信扫码登录会出错
            user_hr_account = yield self.user_hr_account_ds.get_hr_account(conds={
                "wxuser_id": current_user.wxuser.id
            })
            if user_hr_account:
                user_hr_account_cache = UserHrAccountCache()
                user_hr_account_cache.pub_wx_binding(scan_info.group(1), msg='-1')

            yield self.__opt_help_wxuser(current_user.wxuser.id, current_user, msg)

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用
        if current_user.wechat.id == self.settings.qx_wechat_id and msg.EventKey:
            # 临时二维码处理逻辑, 5位type+27为自定义id
            int_scene_id = re.match(r'(\d+)', msg.EventKey)
            if int_scene_id:
                # TODO
                yield self._do_weixin_qrcode(msg)

        raise gen.Return()

    @gen.coroutine
    def __opt_help_wxuser(self, wxuser_id, current_user, msg):
        """
        处理仟寻招聘助手的逻辑
        :param wxuser:
        :param current_user:
        :param msg:
        :return:
        """

        # 关注仟寻招聘助手时，将 user_hr_account.wxuser_id 与 wxuser 绑定
        user_hr_account_cache = UserHrAccountCache()
        if current_user.wechat.id == self.settings.help_wechat_id and msg.EventKey:
            try:
                scan_info = re.match(r'qrscene_([0-9]*)_([0-9]*)_([0-9]*)', msg['EventKey'])
                # 扫码换绑
                if scan_info.group(1) and int(scan_info.group(3)) == 1:
                    yield self.user_hr_account_ds.update_hr_account(
                        conds={
                            "id": int(scan_info.group(1))
                        }, fields={
                            "wxuser_id": wxuser_id
                        })
                # 初次绑定
                elif scan_info.group(1):
                    yield self.user_hr_account_ds.update_hr_account(
                        conds={
                            "id": int(scan_info.group(1)),
                            "wxuser_id": ['NULL', 'is']
                        }, fields={
                            "wxuser_id": wxuser_id
                        })

                # 更新 user_hr_account 的缓存, HR招聘管理平台使用,需同时更新 wxuser_id 和 wxuser
                wxuser = yield self.user_wx_user_ds.get_wxuser({
                    "id": wxuser_id,
                })
                user_hr_account_cache.update_user_hr_account_session(
                    scan_info.group(1),
                    value={
                        "wxuser_id": int(wxuser_id),
                        "wxuser": wxuser
                    })

                # HR招聘管理平台对于HR 帐号绑定微信长轮训机制，需要实时的将状态返回给 HR 平台
                user_hr_account_cache.pub_wx_binding(scan_info.group(1))
            except Exception as e:
                self.logger.error("[wechat][opt_event_subscribe]binding user_hr_account "
                                  "failed: {}".format(traceback.format_exc()))
                user_hr_account_cache.pub_wx_binding(scan_info.group(1), msg='-1')


    @gen.coroutine
    def __do_weixin_qrcode(self, current_user, msg, is_newbie=False):

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用
        if msg.EventKey:
            # 临时二维码处理逻辑, 5位type+27为自定义id
            int_scene_id = re.match(r'(\d+)', msg.EventKey)
            if not int_scene_id:
                int_scene_id = re.match(r'qrscene_(\d+)', msg.EventKey)

        # 临时二维码处理逻辑, 5位type+27为自定义id
        if current_user.wechat.id == self.settings.qx_wechat_id and int_scene_id:
            int_scene_id = int_scene_id.group(1)
            type = int(bin(int(int_scene_id))[:7],base=2)
            real_id = int(bin(int(int_scene_id))[7:],base=2)
            '''
              type: '11000' = 24 pc端用户解绑, '11001' = 25 pc端用户绑定, 11010=26 注册用二维码. 10000=16, 10001=17,
              见 https://wiki.moseeker.com/weixin.md
            '''
            # 注册用二维码, 如果用户 user_wx_user 已经存在, 是老用户, 返回. 否则, 是新用户
            if type == 26:
                params = {
                    'wechatid': current_user.wechat.id,
                    'scene_id': int_scene_id,
                    'result': json_dumps({
                        "status": 0,
                        "message": msg.RESPONSE_SUCCESS,
                        "data": {
                            "isolduser": '1' if is_newbie else '0',
                            "unionid": current_user.wxuser.unionid,
                        }
                    })
                }
                yield self.infra_user_ds.post_scanresult(params)
                return


    def __encryMsg(self, uncrypt_xml, nonce):
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
