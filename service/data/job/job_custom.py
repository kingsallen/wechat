# coding=utf-8

from tornado import gen
from service.data.base import DataService

class JobCustomDataService(DataService):

    @gen.coroutine
    def get_customs_list(self, conds, fields, options=[], appends=[], index='', params=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_customs_list][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = self.job_custom_dao.fields_map.keys()

        response = yield self.job_custom_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)