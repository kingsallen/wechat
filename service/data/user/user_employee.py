# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class UserEmployeeDataService(DataService):

    @gen.coroutine
    def get_employee(self, conds, fields=None, appends=None):

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_employee][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.user_employee_dao.fields_map.keys())

        response = yield self.user_employee_dao.get_record_by_conds(conds, fields, appends)
        raise gen.Return(response)

    @gen.coroutine
    def update_employee(self, conds, fields=None):

        if not conds or not fields:
            self.logger.warning("Warning:[update_employee][invalid parameters], Detail:[conds: {0}, "
                             "fields: {1}]".format(conds, fields))
            raise gen.Return(False)

        ret = yield self.user_employee_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)

