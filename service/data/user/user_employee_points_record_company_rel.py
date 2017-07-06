# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class UserEmployeePointsRecordCompanyRelDataService(DataService):

    @gen.coroutine
    def get_user_employee_points_record_company_rel(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_user_employee_points_record_company_rel][invalid parameters], Detail:[conds: {0}, type: {1}]"
                .format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.user_employee_points_record_company_rel_dao.fields_map.keys())

        response = yield self.user_employee_points_record_company_rel_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_user_employee_points_record_company_rel_cnt(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning(
                "Warning:[get_user_employee_points_record_company_rel_cnt][invalid parameters], Detail:[conds: {0}, type: {1}]"
                .format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.user_employee_points_record_company_rel_dao.fields_map.keys())

        response = yield self.user_employee_points_record_company_rel_dao.get_cnt_by_conds(conds, fields, appends, index)
        raise gen.Return(response)

    @gen.coroutine
    def create_user_employee_points_record_company_rel(self, fields, options=None):
        options = options or []
        response = yield self.user_employee_points_record_company_rel_dao.insert_record(fields, options)
        raise gen.Return(response)
