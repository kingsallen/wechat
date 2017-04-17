# coding=utf-8

# @Time    : 4/13/17 11:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

from tornado import gen
from handler.base import BaseHandler


class PositionAggregationHandler(BaseHandler):

    """
    聚合列表：职位
    """

    @gen.coroutine
    def get(self):
        pass


class CompanyAggregationHandler(BaseHandler):

    """
    聚合列表：企业+头图
    """

    @gen.coroutine
    def get(self):
        pass
