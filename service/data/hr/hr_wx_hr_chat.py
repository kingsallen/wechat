# coding=utf-8

# @Time    : 10/27/16 14:35
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_hr_chat.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrWxHrChatDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_chat(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_chat][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_wx_hr_chat_dao.fields_map.keys())

        response = yield self.hr_wx_hr_chat_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_chats(self, conds, fields=None, options=None, appends=None, index='', params=None):

        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_chats][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_wx_hr_chat_dao.fields_map.keys())

        response = yield self.hr_wx_hr_chat_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)
