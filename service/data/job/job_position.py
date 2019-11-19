# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict
from util.common.decorator import log_time, log_time


class JobPositionDataService(DataService):

    @log_time(20)
    @gen.coroutine
    def get_position(self, conds, fields=None, appends=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_position][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.job_position_dao.fields_map.keys())

        response = yield self.job_position_dao.get_record_by_conds(conds, fields, appends)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_positions_list(self, conds, fields=None, options=None, appends=None, index='', params=None):

        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_positions_list][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_position_dao.fields_map.keys())

        response = yield self.job_position_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)

    @gen.coroutine
    def update_position(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warning(
                "Warning:[update_position][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(
                    conds, fields))
            raise gen.Return(None)

        ret = yield self.job_position_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)

    @cache(ttl=60)
    @gen.coroutine
    def get_position_cnt(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning(
                "Warning:[get_position_cnt][invalid parameters], Detail:[conds: {0}, "
                "type: {1}]".format(
                    conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_position_dao.fields_map.keys())

        response = yield self.job_position_dao.get_cnt_by_conds(conds, fields, appends, index)
        raise gen.Return(response)
