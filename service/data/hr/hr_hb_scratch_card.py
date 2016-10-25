# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class HrHbScratchCardDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_scratch_card(self, conds, fields=None):
        fields = fields or []

        if self._valid_conds(conds):
            self.logger.warn(
                "Warning:[get_hr_scratch_card][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = list(self.hr_hb_scratch_card_dao.fields_map.keys())

        response = yield self.hr_hb_scratch_card_dao.get_record_by_conds(conds, fields)

        raise gen.Return(response)

    @gen.coroutine
    def create_scratch_card(self, fields, options=None):
        options = options or []

        response = yield self.user_wx_user_dao.insert_record(fields, options)
        raise gen.Return(response)

