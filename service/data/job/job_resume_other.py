# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class JobResumeOtherDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_job_resume_other(self, conds, fields=None):
        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn(
                "Warning:[get_job_resume_other][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            return ObjectDict()

        if not fields:
            fields = list(self.job_resume_other_dao.fields_map.keys())

        response = yield self.job_resume_other_dao.get_record_by_conds(
            conds, fields)
        return response

    @gen.coroutine
    def insert_job_resume_other(self, fields, options=None):
        options = options or []

        response = yield self.job_resume_other_dao.insert_record(
            fields, options)
        return response
