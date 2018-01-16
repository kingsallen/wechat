# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class JobApplicationDataService(DataService):

    # must not cache this func
    @gen.coroutine
    def get_job_application(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_job_application][invalid parameters], Detail:[conds: {0}, type: {1}]".format(
                    conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.job_application_dao.fields_map.keys())

        response = yield self.job_application_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_applied_applications_list(self, conds, fields=None, options=None, appends=None, index='', params=None):
        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_applicaitons_list][invalid parameters], Detail:[conds: {0}, "
                                "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_application_dao.fields_map.keys())

        response = yield self.job_application_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)

    @gen.coroutine
    def get_position_applied_cnt(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning(
                "Warning:[get_position_applied_cnt][invalid parameters], Detail:[conds: {0}, "
                "type: {1}]".format(
                    conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_application_dao.fields_map.keys())

        response = yield self.job_application_dao.get_cnt_by_conds(conds, fields, appends, index)
        raise gen.Return(response)
