# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrWxWechatDataService(DataService):

    @cache(ttl=600)
    @gen.coroutine
    def get_wechat(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_wechat][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_wx_wechat_dao.fields_map.keys())

        response = yield self.hr_wx_wechat_dao.get_record_by_conds(
            conds, fields)

        raise gen.Return(response)
