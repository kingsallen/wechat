# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen

from service.data.base import DataService
from util.common import ObjectDict


class UserUserDataService(DataService):

    @gen.coroutine
    def get_user(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_user][invalid parameters], Detail:[conds: {0}, "
                "type: {1}]".format(
                    conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.user_user_dao.fields_map.keys())

        response = yield self.user_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def create_user(self, fields, options=None):
        options = options or []

        response = yield self.user_user_dao.insert_record(fields, options)
        raise gen.Return(response)

    @gen.coroutine
    def update_user(self, conds, fields):
        try:
            response = yield self.user_user_dao.update_by_conds(
                conds=conds, fields=fields
            )
        except Exception as error:
            self.logger.warning(error)
            raise gen.Return(False)

        raise gen.Return(response)
