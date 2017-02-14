# coding=utf-8

# @Time    : 10/28/16 11:04
# @Author  : panda (panyuxin@moseeker.com)
# @File    : user_employee_points_record.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class UserEmployeePointsRecordDataService(DataService):

    @gen.coroutine
    def get_user_employee_points_record(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_user_employee_points_record][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.user_employee_points_record_dao.fields_map.keys())

        response = yield self.user_employee_points_record_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_user_employee_points_record_cnt(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_user_employee_points_record_cnt][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.user_employee_points_record_dao.fields_map.keys())

        response = yield self.user_employee_points_record_dao.get_cnt_by_conds(conds, fields, appends, index)
        raise gen.Return(response)

    @gen.coroutine
    def get_user_employee_points_record_sum(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_user_employee_points_record_sum][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.user_employee_points_record_dao.fields_map.keys())

        response = yield self.user_employee_points_record_dao.get_sum_by_conds(conds, fields, appends, index)
        raise gen.Return(response)

    @gen.coroutine
    def create_user_employee_points_record(self, fields, options=None):
        options = options or []
        response = yield self.user_employee_points_record_dao.insert_record(fields, options)
        raise gen.Return(response)
