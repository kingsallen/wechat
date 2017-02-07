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
    def get_wechat(self, params):
        """获得微信号信息
        :param params:
        :return:
        """
        ret = yield self.hr_wx_wechat_ds.get_wechat(params)
        raise gen.Return(ret)
