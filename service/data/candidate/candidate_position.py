# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class CandidatePositionDataService(DataService):

    @gen.coroutine
    def get_candidate_position(self, conds, fields=None, options=None, appends=None, index=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        index = index or ''

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_candidate_position][invalid parameters], Detail:["
                                "conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.candidate_position_dao.fields_map.keys())

        response = yield self.candidate_position_dao.get_record_by_conds(conds, fields, options, appends, index)
        raise gen.Return(response)
