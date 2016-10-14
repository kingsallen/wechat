# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from utils.common.decorator import cache


class HrWxWechatDataService(DataService):

    @cache(ttl=600)
    @gen.coroutine
    def get_wechat(self, conds, fields=None):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn(
                "Warning:[get_wechat][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = self.hr_wx_wechat_dao.fields_map.keys()

        response = yield self.hr_wx_wechat_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
