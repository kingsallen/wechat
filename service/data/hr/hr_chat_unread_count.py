# coding=utf-8

# @Time    : 10/28/16 10:08
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_chat_unread_count.py
# @DES     :

from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class HrChatUnreadCountDataService(DataService):

    @gen.coroutine
    def get_chat_unread_count(self, conds, fields=None, options=None, appends=None):

        fields = fields or []
        options = options or []
        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn(
                "Warning:[get_chat_unread_count][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            return ObjectDict()

        if not fields:
            fields = list(self.hr_chat_unread_count_dao.fields_map.keys())

        response = yield self.hr_chat_unread_count_dao.get_record_by_conds(
            conds, fields, options, appends)
        return response

    @gen.coroutine
    def get_chat_unread_count_cnt(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_chat_unread_count_cnt][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_chat_unread_count_dao.fields_map.keys())

        response = yield self.hr_chat_unread_count_dao.get_cnt_by_conds(conds, fields, appends, index)
        raise gen.Return(response)
