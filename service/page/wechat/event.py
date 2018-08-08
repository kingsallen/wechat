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
import conf.message as message
from cache.user.user_hr_account import UserHrAccountCache
from service.page.base import PageService
from util.wechat.msgcrypt import WXBizMsgCrypt
from util.tool.url_tool import make_static_url
from util.tool.date_tool import curr_now
from util.tool.str_tool import mobile_validate
from util.common import ObjectDict
from util.tool.json_tool import json_dumps
from util.wechat.core import get_wxuser


class EventPageService(PageService):

    def __init__(self):
        super().__init__()

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
            res = yield getattr(self, "rep_{}".format(rule.module))(msg, rule.id, nonce, wechat)
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
                make_static_url(replie.thumb, ensure_protocol=True),
                replie.url
            )
            news += item

        news_info = news + wx_const.WX_NEWS_REPLY_FOOT_TPL

        if wechat.third_oauth == 1:
            # 第三方授权方式
            news_info = self.__encryMsg(news_info, nonce)

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
        keyword_head = keyword.split(" ")[0]

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
            res = yield getattr(self, "rep_{}".format(rule.module))(msg, rule.id, nonce, wechat)
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
            res = yield getattr(self, "rep_{}".format(rule.module))(msg, rule.id, nonce, wechat)
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

        if not openid:
            self.logger.error("[wechat_oauth][opt_event_subscribe] openid is: (%s)." % openid)
            raise gen.Return()

        wxuser = yield get_wxuser(current_user.wechat.access_token, openid)

        if not wxuser:
            self.logger.error("[wechat_oauth][opt_event_subscribe] wxuser is: (%s)." % wxuser)
            raise gen.Return()

        if wxuser.get('qr_scene_str'): # 场景二维码处理
            if 'wechat_permanent_qr-' in wxuser.get('qr_scene_str'):  # 永久二维码扫描关注标志字符串

                _, wechat_id = wxuser.get('qr_scene_str').split('-')
                self.logger.info(json_dumps(dict(
                    wechat_id=wechat_id,
                    openid=openid,
                    qr_scene_str=wxuser.get('qr_scene_str'),
                    is_permanent_qr_subscribe=1
                )))

        is_newbie = False
        if not current_user.wxuser:
            # 新微信用户
            is_newbie = True
            wxuser_id = yield self._create_wxuser(openid, current_user, wxuser)

            yield self.__opt_help_wxuser(wxuser_id, current_user, msg)

        else:
            # 老微信用户
            yield self._update_wxuser(openid, current_user, msg, wxuser)

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用,以及Mars EDM活动
        if current_user.wechat.id in (self.settings.qx_wechat_id, const.MARS_ID) and msg.EventKey:
            # 临时二维码处理逻辑, 5位type+27为自定义id
            yield self._do_weixin_qrcode(current_user.wechat, msg, is_newbie=is_newbie)

        res = yield self.opt_follow(msg, current_user.wechat, nonce)
        raise gen.Return(res)

    @gen.coroutine
    def _create_wxuser(self, openid, current_user, wechat_userinfo):
        """
        创建微信 wxuser 用户
        :param openid:
        :param current_user:
        :return:
        """
        wxuser_id = current_user.wxuser.id

        # 已授权给仟寻，或者 HR 雇主平台的用户，已经创建了 wxuser，故不需要再创建 wxuser
        if (current_user.wechat.id == self.settings.helper_wechat_id
            or current_user.wechat.id == self.settings.qx_wechat_id) and current_user.wxuser:
            res = yield self.user_wx_user_ds.update_wxuser(
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
                    "subscribe_time" : current_user.wxuser.subscribe_time or curr_now(),
                    "unsubscibe_time": None,
                    "source":          const.WX_USER_SOURCE_UPDATE_SHORT
                })

        if not current_user.wxuser:
            wxuser_id = yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe":    const.WX_USER_SUBSCRIBED,
                "openid":          openid,
                "nickname":        wechat_userinfo.nickname or "",
                "sex":             wechat_userinfo.sex or 0,
                "city":            wechat_userinfo.city or 0,
                "country":         wechat_userinfo.country or "",
                "province":        wechat_userinfo.province or "",
                "language":        wechat_userinfo.language or "",
                "headimgurl":      wechat_userinfo.headimgurl or "",
                "wechat_id":       current_user.wechat.id,
                "unionid":         wechat_userinfo.unionid or "",
                "subscribe_time":  curr_now(),
                "unsubscibe_time": None,
                "source":          const.WX_USER_SOURCE_SUBSCRIBE
            })
        raise gen.Return(wxuser_id)

    @gen.coroutine
    def _update_wxuser(self, openid, current_user, msg, wechat_userinfo):
        """
        更新老微信 wxuser 信息
        :param openid:
        :param current_user:
        :param msg:
        :return:
        """

        res = yield self.user_wx_user_ds.update_wxuser(
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
                "subscribe_time":  current_user.wxuser.subscribe_time or curr_now(),
                "unsubscibe_time": None,
                "source":          const.WX_USER_SOURCE_UPDATE_ALL
            })

        yield self.__opt_help_wxuser(current_user.wxuser.id, current_user.wechat, msg)

        raise gen.Return()

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
            res = yield self.user_wx_user_ds.update_wxuser(
                conds={"id": current_user.wxuser.id},
                fields={
                    "is_subscribe":    const.WX_USER_UNSUBSCRIBED,
                    "unsubscibe_time": current_user.wxuser.subscribe_time or curr_now(),
                    "subscribe_time":  None,
                    "source":          const.WX_USER_SOURCE_UNSUBSCRIBE
                })
            # 取消关注仟寻招聘助手时，将user_hr_account.wxuser_id与user_wx_user.id 解绑
            if current_user.wechat.id == self.settings.helper_wechat_id:
                user_hr_account = yield self.user_hr_account_ds.get_hr_account(conds={
                    "wxuser_id": current_user.wxuser.id
                })

                if user_hr_account:
                    yield self.user_hr_account_ds.update_hr_account(
                        conds={
                            "wxuser_id": current_user.wxuser.id
                        }, fields={
                            "wxuser_id": None
                        })
                    user_hr_account_cache = UserHrAccountCache()
                    user_hr_account_cache.update_user_hr_account_session(
                        user_hr_account.id,
                        value = ObjectDict(
                            wxuser_id = 0,
                            wxuser = ObjectDict()
                        ))

        raise gen.Return()

    @gen.coroutine
    def opt_event_scan(self, current_user, msg):
        """
        处理用户扫码事件
        :param current_user:
        :param msg:
        :return:
        """

        if current_user.wechat.id == self.settings.helper_wechat_id and msg.EventKey:
            scan_info = re.match(r"([0-9]*)_([0-9]*)_([0-9]*)", msg.EventKey)


            # 已绑定过的微信号，不能再绑定第二个hr_account账号，否则微信扫码登录会出错
            user_hr_account = yield self.user_hr_account_ds.get_hr_account(conds={
                "wxuser_id": current_user.wxuser.id
            })

            if user_hr_account:
                user_hr_account_cache = UserHrAccountCache()
                user_hr_account_cache.pub_wx_binding(int(scan_info.group(1)), msg="-1")
                raise gen.Return()

            yield self.__opt_help_wxuser(current_user.wxuser.id, current_user.wechat, msg)

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用,以及Mars EDM活动
        if current_user.wechat.id in (self.settings.qx_wechat_id, const.MARS_ID) and msg.EventKey:
            # 临时二维码处理逻辑, 5位type+27为自定义id
            yield self._do_weixin_qrcode(current_user.wechat, msg)

        raise gen.Return()

    @gen.coroutine
    def __opt_help_wxuser(self, wxuser_id, wechat, msg):
        """
        处理仟寻招聘助手的逻辑
        :param wxuser:
        :param wechat:
        :param msg:
        :return:
        """

        self.logger.debug("[__opt_help_wxuser] wxuser_id: {0}, wechat:{1}, msg:{2}".format(wxuser_id, wechat, msg))

        # 关注仟寻招聘助手时，将 user_hr_account.wxuser_id 与 wxuser 绑定
        if wechat.id == self.settings.helper_wechat_id and msg.EventKey:
            user_hr_account_cache = UserHrAccountCache()

            res = None
            scan_info = None

            try:
                scan_info = re.match(r"qrscene_([0-9]*)_([0-9]*)_([0-9]*)", msg.EventKey)
                if not scan_info:
                    scan_info = re.match(r"([0-9]*)_([0-9]*)_([0-9]*)", msg.EventKey)

                hr_account_id = int(scan_info.group(1))
                scan_type = int(scan_info.group(3))

                # from yiliang: 不清楚这两种区别是什么，为什么要这么写，以及是否还有其他情况
                # 扫码换绑
                if hr_account_id and scan_type == 1:
                    res = yield self.user_hr_account_ds.update_hr_account(
                        conds={ "id": hr_account_id },
                        fields={ "wxuser_id": wxuser_id })

                # 普通扫码绑定
                elif hr_account_id:
                    res = yield self.user_hr_account_ds.update_hr_account(
                        conds={ "id": hr_account_id },
                        fields={ "wxuser_id": wxuser_id })

                # from yiliang: 是否可以这样：
                # else:
                #     assert False # should not be here
                #     user_hr_account_cache.pub_wx_binding(scan_info.group(1), msg="-1")

                # 更新 user_hr_account 和 user_wx_user 的关系成功后, 更新 user_hr_account 的缓存, HR招聘管理平台使用, 需同时更新 wxuser_id 和 wxuser
                wxuser = yield self.user_wx_user_ds.get_wxuser(conds={"id": wxuser_id})

                user_hr_account_cache.update_user_hr_account_session(
                    hr_id=hr_account_id,
                    value=ObjectDict(
                        wxuser_id=wxuser_id,
                        wxuser=wxuser
                    ))

                # HR招聘管理平台对于HR 帐号绑定微信长轮训机制，需要实时的将状态返回给 HR 平台
                user_hr_account_cache.pub_wx_binding(scan_info.group(1))

            except Exception as e:
                self.logger.error("[wechat][opt_event_subscribe]binding user_hr_account "
                                  "failed: {}".format(traceback.format_exc()))
                user_hr_account_cache.pub_wx_binding(scan_info.group(1), msg="-1")

        raise gen.Return()

    @gen.coroutine
    def _do_weixin_qrcode(self, wechat, msg, is_newbie=False):

        self.logger.info("[_do_weixin_qrcode] wechat:{0}, msg:{1}, is_newbie:{2}".format(wechat, msg, is_newbie))

        # 处理临时二维码，目前主要在 PC 上创建帐号、绑定账号时使用
        int_scene_id = ""
        if msg.EventKey:
            # 临时二维码处理逻辑, 5位type+27为自定义id
            int_scene_id = re.match(r"(\d+)", msg.EventKey)
            if not int_scene_id:
                int_scene_id = re.match(r"qrscene_(\d+)", msg.EventKey)

        # 取最新的微信用户信息
        wxuser = yield self.user_wx_user_ds.get_wxuser(conds={
            "openid": msg.FromUserName,
            "wechat_id": wechat.id
        })

        # 临时二维码处理逻辑, 5位type+27为自定义id
        if wechat.id in (self.settings.qx_wechat_id, const.MARS_ID) and int_scene_id:
            int_scene_id = int_scene_id.group(1)
            type = int(bin(int(int_scene_id))[:7],base=2)
            real_user_id = int(bin(int(int_scene_id))[7:],base=2)
            """
              type: 
              "11000" = 24 pc端用户解绑,
              "11001" = 25 pc端用户绑定,
               11010=26 pc注册用二维码，
               11011 =27 pc扫码修改手机。 
               
              hr 端 10000=16, 10001=17,
              11111=31  Mars EDM活动二维码
              见 https://wiki.moseeker.com/weixin.md
            """

            if type == 26:
                # 注册用二维码
                params = {
                    "wechatid": wechat.id,
                    "scene_id": int_scene_id,
                    "result": json_dumps({
                        "status": 0,
                        "message": message.RESPONSE_SUCCESS,
                        "data": {
                            "isolduser": "1" if is_newbie else "0",
                            "unionid": wxuser.unionid,
                        }
                    })
                }

                yield self.infra_user_ds.post_scanresult(params)
                raise gen.Return()

            elif type == 25:
                # PC端用户绑定
                if wxuser.sysuser_id:
                    user_record = yield self.user_user_ds.get_user({
                        "unionid": wxuser.unionid,
                        "parentid": 0  # 保证查找正常的 user record
                    })
                    if user_record.id != real_user_id and mobile_validate(user_record.username):
                        params = {
                                "wechatid": wechat.id,
                                "scene_id": int_scene_id,
                                "result": json_dumps({
                                    "status": 4,
                                    "message": message.WECHAT_SCAN_HAD_BINDED
                                })
                            }
                        yield self.infra_user_ds.post_scanresult(params)
                        raise gen.Return()

                if self.__user_bind_wx(wxuser, real_user_id):
                    params = {
                            "wechatid": wechat.id,
                            "scene_id": int_scene_id,
                            "result": json_dumps({
                                "status": 0,
                                "message": message.RESPONSE_SUCCESS,
                                "data": wxuser.unionid,
                            })
                        }
                    yield self.infra_user_ds.post_scanresult(params)
                    raise gen.Return()
                else:
                    params = {
                            "wechatid": wechat.id,
                            "scene_id": int_scene_id,
                            "result": json_dumps({
                                "status": 5,
                                "message": message.WECHAT_SCAN_FAILED
                            })
                        }
                    yield self.infra_user_ds.post_scanresult(params)
                    raise gen.Return()

            elif type == 24 or type == 27:
                # pc端用户解绑,pc扫码修改手机
                if wxuser:
                    # 验证扫描者的openid(FromUserName)是否与EventKey里面隐含的user_id匹配
                    # 不匹配, 表示被其他帐号扫描了, 提示非本人扫描的提示
                    if wxuser.sysuser_id == real_user_id:
                        params = {
                                "wechatid":  wechat.id,
                                "scene_id":int_scene_id,
                                "result": json_dumps({
                                    "status": 0,
                                    "message": message.RESPONSE_SUCCESS
                                })
                            }
                        yield self.infra_user_ds.post_scanresult(params)
                        raise gen.Return()
                    else:
                        params = {
                                "wechatid": wechat.id,
                                "scene_id": int_scene_id,
                                "result": json_dumps({
                                    "status": 2,
                                    "message": message.WECHAT_SCAN_CHANGE_WECHAT
                                })
                            }
                        yield self.infra_user_ds.post_scanresult(params)
                        raise gen.Return()

                else:
                    # 扫描用户不存在, 可以认为是非用户本人扫描了二维码
                    params = {
                            "wechatid": wechat.id,
                            "scene_id": int_scene_id,
                            "result": json_dumps({
                                "status": 3,
                                "message": message.WECHAT_SCAN_CHANGE_WECHAT
                            })
                        }
                    yield self.infra_user_ds.post_scanresult(params)
                    raise gen.Return()
            elif type == 31:
                # Mars EDM活动的用户，与EDM数据表关联起来
                user = yield self.campaign_mars_edm_subscribe_ds.get_mars_user({
                    "id": real_user_id
                })
                if user:
                    yield self.campaign_mars_edm_subscribe_ds.update_mars_user(
                        conds={"id": real_user_id},
                        fields={"wxuser_id": wxuser.id}
                    )

            elif type == 16:
                pass
            elif type == 17:
                pass

        raise gen.Return()

    @gen.coroutine
    def __user_bind_wx(self, wxuser, user_id):
        """
        更新unionid, nickname
        :param wxuser:
        :param user_id:
        :return:
        """
        if wxuser.unionid:
            res = yield self.user_user_ds.update_user(
                conds={"id": user_id},
                fields={
                    "nickname": wxuser.nickname,
                })
            raise gen.Return(True)
        raise gen.Return(False)

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
