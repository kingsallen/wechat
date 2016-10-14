# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from utils.common.decorator import cache

class HrCompanyConfDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_company_conf(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_company_conf][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = self.hr_company_conf_dao.fields_map.keys()

        response = yield self.hr_company_conf_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
