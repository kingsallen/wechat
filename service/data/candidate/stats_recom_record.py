# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class StatsRecomRecordDataService(DataService):
    @cache(ttl=60)
    @gen.coroutine
    def get_stats_recom_record(self, conds, fields=None, options=None, appends=None, index=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        index = index or ''

        if not self._valid_conds(conds):
            self.logger.warn(
                "Warning:[get_stats_share_record][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(
                self.stats_recom_record_dao.fields_map.keys())

        response = yield self.stats_recom_record_dao.get_record_by_conds(
            conds, fields, options, appends,
            index)
        raise gen.Return(response)

    @gen.coroutine
    def insert_stats_recom_record(self, fields, options=None):
        options = options or []

        response = yield self.stats_recom_record_dao.insert_record(fields,
                                                                  options)
        raise gen.Return(response)
