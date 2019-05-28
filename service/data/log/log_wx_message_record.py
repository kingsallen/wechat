# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class LogWxMessageRecordDataService(DataService):

    @gen.coroutine
    def get_wx_message_log_record(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_wx_message_log_record][invalid parameters], \
                    Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.log_wx_message_record_dao.fields_map.keys())

        response = yield self.log_wx_message_record_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def create_wx_message_log_record(self, fields, options=None):
        options = options or []

        response = yield self.log_wx_message_record_dao.insert_record(fields,
                                                                   options)
        raise gen.Return(response)

