# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict
from util.wechat.core import get_temporary_qrcode
import conf.common as const


class WechatPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_wechat(self, conds, fields=[]):

        """
        获得公众号信息
        :param conds:
        :param fields: 示例:
        conds = {
            "id": wechat_id
            "signature": signature
        }
        :return:
        """

        wechat = yield self.hr_wx_wechat_ds.get_wechat(conds, fields)

        raise gen.Return(wechat)

    @gen.coroutine
    def get_wechat_theme(self, conds, fields=[]):

        """
        获得公众号主题色信息
        :param conds:
        :param fields:
        :return:
        """

        theme = yield self.config_sys_theme_ds.get_theme(conds, fields)
        raise gen.Return(theme)

    @gen.coroutine
    def get_wechat_info(self, current_user, pattern_id, in_wechat):
        """
        获取公众号相关信息
        """
        wechat = ObjectDict()
        wechat.subscribed = True if current_user.wxuser.is_subscribe or current_user.wechat.type == 0 or not in_wechat else False
        wechat.qrcode = yield get_temporary_qrcode(wechat=current_user.wechat,
                                                   pattern_id=pattern_id)
        wechat.name = current_user.wechat.name
