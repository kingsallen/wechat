# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict

class JobOccupationDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_occupation(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_occupation][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.job_occupation_dao.fields_map.keys())

        response = yield self.job_occupation_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_occupations_list(self, conds, fields, options=[], appends=[], index='', params=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_occupations_list][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_occupation_dao.fields_map.keys())

        response = yield self.job_occupation_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)