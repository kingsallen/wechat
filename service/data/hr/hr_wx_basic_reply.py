# coding=utf-8

# @Time    : 10/27/16 14:35
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_basic_reply.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrWxBasicReplyDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_wx_basic_reply(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn("Warning:[get_wx_basic_reply][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_wx_basic_reply_dao.fields_map.keys())

        response = yield self.hr_wx_basic_reply_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
