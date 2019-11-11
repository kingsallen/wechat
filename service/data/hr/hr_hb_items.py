# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import log_core


class HrHbItemsDataService(DataService):

    @gen.coroutine
    def get_hb_items(self, conds, fields=None,options=None, appends=None,
                     index=None):
        fields = fields or []

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_hb_items][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_hb_items_dao.fields_map.keys())

        response = yield self.hr_hb_items_dao.get_record_by_conds(
            conds, fields, options, appends, index)

        raise gen.Return(response)

    @gen.coroutine
    def get_hb_items_list(self, conds, fields, options=None, appends=None, index='', params=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_hb_items_list][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_hb_items_dao.fields_map.keys())

        response = yield self.hr_hb_items_dao.get_list_by_conds(
            conds, fields, options, appends, index, params)

        raise gen.Return(response)

    @log_core
    @gen.coroutine
    def update_hb_items(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warning(
                "Warning:[update_hb_items][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(
                    conds, fields))
            raise gen.Return(None)

        ret = yield self.hr_hb_items_dao.update_by_conds(conds=conds, fields=fields)

        raise gen.Return(ret)

    @gen.coroutine
    def create_hb_items(self, fields, options=None):
        options = options or []

        response = yield self.hr_hb_items_dao.insert_record(fields, options)
        raise gen.Return(response)

    @gen.coroutine
    def get_hb_items_amount_sum(self, conds, fields, appends=None, index=''):

        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning(
                "Warning:[get_hb_items_amount_sum][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = list(
                self.hr_hb_items_dao.fields_map.keys())

        response = yield self.hr_hb_items_dao.get_sum_by_conds(
            conds, fields, appends, index)

        raise gen.Return(response)
