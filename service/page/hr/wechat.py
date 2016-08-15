# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService

class WechatPageService(PageService):

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