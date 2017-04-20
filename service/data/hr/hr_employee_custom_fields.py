# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrEmployeeCustomFieldsDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_employee_custom_field_record(self, conds, fields=None, options=None, appends=None):

        fields = fields or []
        options = options or []
        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn(
                "Warning:[get_employee_custom_field_record][invalid parameters], "
                "Detail:[conds: {0}, "
                "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_employee_custom_fields_dao.fields_map.keys())

        response = yield self.hr_employee_custom_fields_dao.get_record_by_conds(conds, fields, options, appends)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_employee_custom_field_records(self, conds, fields=None, options=None, appends=None):

        fields = fields or []
        options = options or []
        appends = appends or []

        if not self._valid_conds(conds):
            self.logger.warn(
                "Warning:[get_hr_hb_position_binding_list][invalid "
                "parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_employee_custom_fields_dao.fields_map.keys())

        response = yield self.hr_employee_custom_fields_dao.get_list_by_conds(
            conds, fields, options, appends)

        raise gen.Return(response)

    @gen.coroutine
    def update_employee_custom_fields(self, conds, fields):
        try:
            response = yield self.hr_employee_custom_fields_dao.update_by_conds(
                conds=conds, fields=fields
            )
        except Exception as error:
            self.logger.warning(error)
            raise gen.Return(False)

        raise gen.Return(response)
