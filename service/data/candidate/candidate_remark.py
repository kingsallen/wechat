# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class CandidateRemarkDataService(DataService):
    @cache(ttl=60)
    @gen.coroutine
    def get_candidate_remark(self, conds, fields=None, options=None, appends=None, index=None):
        options = options or []
        appends = appends or []
        index = index or ''

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_candidate_remark][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(
                self.candidate_remark_dao.fields_map.keys())

        response = yield self.candidate_remark_dao.get_record_by_conds(
            conds, fields, options, appends,
            index)
        raise gen.Return(response)

    @gen.coroutine
    def update_candidate_remark(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warning(
                "Warning:[update_candidate_remark][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(False)

        ret = yield self.candidate_remark_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)
