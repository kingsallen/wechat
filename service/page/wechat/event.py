# coding=utf-8

# @Time    : 2/7/17 15:38
# @Author  : panda (panyuxin@moseeker.com)
# @File    : event.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

from service.page.base import PageService

class EventPageService(PageService):

    @gen.coroutine
    def get_wxuser_by_openid(self, openid, wechat_id):
        """根据 openid 和 wechat_id 获取 wxuser
        :param openid:
        :param wechat_id
        :return:
        """

        ret = yield self.user_wx_user_ds.get_wxuser(conds={
            "wechat_id": wechat_id,
            "openid":    openid
        })
        raise gen.Return(ret)
