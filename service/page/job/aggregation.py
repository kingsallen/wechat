# coding=utf-8

# @Time    : 4/18/17 11:57
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

from tornado import gen
from service.page.base import PageService

class LandingPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_aggregation_banner(self):

        """
        获得聚合号列表页 banner 头图
        :return:
        """

        banner_res = yield self.thrift_position_ds.get_aggregation_banner()
        raise gen.Return(banner_res)

    @gen.coroutine
    def get_hot_company(self, params):




