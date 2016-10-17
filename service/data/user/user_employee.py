# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class UserEmployeeDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_employee(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_employee][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = self.user_employee_dao.fields_map.keys()

        response = yield self.user_employee_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

