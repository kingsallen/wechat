# coding=utf-8


from tornado import gen
from service.data.base import DataService


class HrHbSendRecordDataService(DataService):

    @gen.coroutine
    def insert_record(self, fields, options=None):
        options = options or []

        response = yield self.hr_hb_send_record_dao.insert_record(fields, options)
        raise gen.Return(response)

