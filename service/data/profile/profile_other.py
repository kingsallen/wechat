# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class ProfileOtherDataService(DataService):

    @gen.coroutine
    def get_profile_other(self, conds, fields=None, appends=None):

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_profile_other][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.profile_other_dao.fields_map.keys())

        response = yield self.profile_other_dao.get_record_by_conds(
            conds=conds, fields=fields, appends=appends)
        raise gen.Return(response)

    @gen.coroutine
    def update_profile_other(self, conds, fields=None):

        if not conds or not fields:
            self.logger.warning("Warning:[update_profile_other][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(False)

        ret = yield self.profile_other_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)

    @gen.coroutine
    def insert_profile_other(self, fields, options=None):
        options = options or []

        response = yield self.profile_other_dao.insert_record(
            fields, options)

        raise gen.Return(response)
