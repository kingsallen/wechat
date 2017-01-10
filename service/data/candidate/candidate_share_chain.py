# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class CandidateShareRecordDataService(DataService):

    @gen.coroutine
    def get_share_chain(self, conds, fields=None, options=None, appends=None,
                        index=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        index = index or ''

        if not self._valid_conds(conds):
            self.logger.warn(
                "Warning:[get_share_chain][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]"
                .format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.candidate_share_chain_dao.fields_map.keys())

        response = yield self.candidate_share_chain_dao.get_record_by_conds(
            conds, fields, options, appends, index)
        raise gen.Return(response)

    @gen.coroutine
    def insert_share_chain(self, fields, options=None):
        options = options or []

        response = yield self.candidate_share_chain_dao.insert_record(
            fields, options)
        raise gen.Return(response)
