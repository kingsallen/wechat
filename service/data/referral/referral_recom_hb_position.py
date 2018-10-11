# coding=utf-8


from tornado import gen
from service.data.base import DataService


class ReferralRecomHbPositionDataService(DataService):

    @gen.coroutine
    def create_recom_hb_position(self, fields, options=None):
        options = options or []

        response = yield self.referral_recom_hb_position_dao.insert_record(fields, options)
        raise gen.Return(response)
