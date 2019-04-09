# coding=utf-8


from tornado import gen
from service.data.base import DataService


class LogDatagroupPrepareDataDataService(DataService):

    @gen.coroutine
    def create_qrcode_subscribe_record(self, fields, options=None):
        options = options or []

        response = yield self.log_datagroup_prepare_data_dao.insert_record(fields, options)
        raise gen.Return(response)

