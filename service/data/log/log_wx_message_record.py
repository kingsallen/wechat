# coding=utf-8


from tornado import gen
from service.data.base import DataService


class LogWxMessageRecordDataService(DataService):

    @gen.coroutine
    def create_wx_message_log_record(self, fields, options=None):
        options = options or []

        response = yield self.log_wx_message_record_dao.insert_record(fields,
                                                                   options)
        raise gen.Return(response)

