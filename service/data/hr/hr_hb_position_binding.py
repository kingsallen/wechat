# coding=utf-8


from tornado import gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from util.common.decorator import log_core


class HrHbPositionBindingDataService(DataService):
    @cache(ttl=60)
    @gen.coroutine
    def get_hr_hb_position_binding(self, conds, fields=None):
        fields = fields or []

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_hr_hb_position_binding][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_hb_position_binding_dao.fields_map.keys())

        response = yield self.hr_hb_position_binding_dao.get_record_by_conds(
            conds, fields)

        raise gen.Return(response)

    @log_core
    @gen.coroutine
    def get_hr_hb_position_binding_list(self, conds, fields=None, options=None,
                                        appends=None, index='', params=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_hr_hb_position_binding_list][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_hb_position_binding_dao.fields_map.keys())

        response = yield self.hr_hb_position_binding_dao.get_list_by_conds(
            conds, fields, options, appends, index, params)

        raise gen.Return(response)
