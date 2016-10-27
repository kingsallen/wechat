# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class JobApplicationDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_job_application(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_job_application][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.job_application_dao.fields_map.keys())

        response = yield self.job_application_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
