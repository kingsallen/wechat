# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class HrWxTemplateMessageDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_wx_template(self, conds, fields=None,options=None, appends=None,
                        index=None):

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_wx_template][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = list(self.hr_wx_template_message_dao.fields_map.keys())

        response = yield self.hr_wx_template_message_dao.get_record_by_conds(
            conds, fields, options, appends, index)

        raise gen.Return(response)
