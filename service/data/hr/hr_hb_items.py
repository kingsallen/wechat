# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrHbItemsDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_hb_items(self, conds, fields=None,options=None, appends=None,
                     index=None):
        fields = fields or []

        if self._valid_conds(conds):
            self.logger.warn("Warning:[get_hb_items][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_hb_items_dao.fields_map.keys())

        response = yield self.hr_hb_items_dao.get_record_by_conds(
            conds, fields, options, appends, index)

        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_hb_items_list(self, conds, fields, options=None,
                              appends=None, index='', params=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if self._valid_conds(conds):
            self.logger.warn("Warning:[get_hb_items_list][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_hb_items_dao.fields_map.keys())

        response = yield self.hr_hb_items_dao.get_list_by_conds(
            conds, fields, options, appends, index, params)

        raise gen.Return(response)
