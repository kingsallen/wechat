# coding=utf-8

# @Time    : 10/26/16 18:17
# @Author  : panda (panyuxin@moseeker.com)
# @File    : job_position_ext.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict
from util.common.decorator import log_time, log_time


class JobPositionExtDataService(DataService):

    @log_time(20)
    @cache(ttl=60)
    @gen.coroutine
    def get_position_ext(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_position_ext][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.job_position_ext_dao.fields_map.keys())

        response = yield self.job_position_ext_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_position_ext_list(self, conds, fields=None, options=None, appends=None, index='', params=None):

        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_positions_ext_list][invalid parameters], Detail:[conds: {0}, "
                                "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_position_ext_dao.fields_map.keys())

        response = yield self.job_position_ext_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)
