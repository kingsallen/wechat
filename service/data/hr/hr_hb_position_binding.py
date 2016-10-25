# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class HrHbPositionBindingDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_hr_hb_position_binding(self, conds, fields=None):
        fields = fields or []

        if self._valid_conds(conds):
            self.logger.warn("Warning:[get_hr_hb_config][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = list(self.hr_hb_position_binding_dao.fields_map.keys())

        response = yield self.hr_hb_position_binding_dao.get_record_by_conds(
            conds, fields)

        raise gen.Return(response)
