# coding=utf-8


from tornado import gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import log_core


class HrHbConfigDataService(DataService):
    @gen.coroutine
    def get_hr_hb_config(self, conds, fields=None, appends=None):

        fields = fields or []

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_hr_hb_config][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds,
                                                                                                        type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_hb_config_dao.fields_map.keys())

        response = yield self.hr_hb_config_dao.get_record_by_conds(
            conds=conds, fields=fields, appends=appends)

        raise gen.Return(response)

    @log_core
    @gen.coroutine
    def get_hr_hb_config_list(self, conds, fields=None, options=None,
                              appends=None, index='', params=None):
        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_hr_hb_position_binding_list][invalid "
                "parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_hb_config_dao.fields_map.keys())

        response = yield self.hr_hb_config_dao.get_list_by_conds(
            conds, fields, options, appends, index, params)

        raise gen.Return(response)

    @gen.coroutine
    def update_hr_hb_config(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warning(
                "Warning:[update_hr_hb_config][invalid parameters], Detail:["
                "conds: {0}, fields: {1}]".format(
                    conds, fields))
            raise gen.Return(None)

        ret = yield self.hr_hb_config_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)
