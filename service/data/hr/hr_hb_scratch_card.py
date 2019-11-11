# coding=utf-8


from tornado import gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import log_core


class HrHbScratchCardDataService(DataService):
    @log_core
    @gen.coroutine
    def get_scratch_card(self, conds, fields=None):
        fields = fields or []

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_hr_scratch_card][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds,
                                                                                                           type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_hb_scratch_card_dao.fields_map.keys())

        response = yield self.hr_hb_scratch_card_dao.get_record_by_conds(conds, fields)

        raise gen.Return(response)

    @log_core
    @gen.coroutine
    def create_scratch_card(self, fields, options=None):
        options = options or []

        response = yield self.hr_hb_scratch_card_dao.insert_record(fields, options)
        raise gen.Return(response)

    @log_core
    @gen.coroutine
    def update_scratch_card(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warning(
                "Warning:[update_scratch_card][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(
                    conds, fields))
            raise gen.Return(None)

        ret = yield self.hr_hb_scratch_card_dao.update_by_conds(conds=conds, fields=fields)

        raise gen.Return(ret)
