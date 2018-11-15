# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class CandidateCompanyDataService(DataService):

    @gen.coroutine
    def get_candidate_company(
            self,
            conds,
            fields=None,
            options=None,
            appends=None,
            index=None):
        options = options or []
        appends = appends or []
        index = index or ''

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_candidate_company][invalid parameters], Detail:[conds: {0}, type: {1}]".format(
                    conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(
                self.candidate_company_dao.fields_map.keys())

        response = yield self.candidate_company_dao.get_record_by_conds(
            conds, fields, options, appends,
            index)
        raise gen.Return(response)

    @gen.coroutine
    def update_candidate_company(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warning(
                "Warning:[update_candidate_company][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(
                    conds, fields))
            raise gen.Return(False)

        ret = yield self.candidate_company_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)

    @gen.coroutine
    def insert_candidate_company(self, fields, options=None):
        options = options or []

        response = yield self.candidate_company_dao.insert_record(fields,
                                                                   options)
        raise gen.Return(response)
