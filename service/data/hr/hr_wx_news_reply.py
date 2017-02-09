# coding=utf-8

# @Time    : 10/27/16 14:35
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_basic_reply.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class HrWxNewsReplyDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_wx_news_replys(self, conds, fields=None, options=None, appends=None, index='', params=None):

        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_wx_news_replys][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_wx_news_reply_dao.fields_map.keys())

        response = yield self.hr_wx_news_reply_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)
