# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class HrHbItemsDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_hb_items(self, conds, fields=None):
        fields = fields or []

        if self._valid_conds(conds):
            self.logger.warn("Warning:[get_hb_items][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = list(self.hr_hb_items_dao.fields_map.keys())

        response = yield self.hr_hb_items_dao.get_record_by_conds(
            conds, fields)

        raise gen.Return(response)
