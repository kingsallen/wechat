# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict

class HrCompanyConfDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_company_conf(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_company_conf][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_company_conf_dao.fields_map.keys())

        response = yield self.hr_company_conf_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_company_teamname_custom(self, company_id):
        teamname_custom = yield self.get_company_conf({"company_id": company_id}, fields=["teamname_custom"])
        if not (teamname_custom and teamname_custom["teamname_custom"].strip()):
            teamname_custom = {'teamname_custom': self.constant.TEAMNAME_CUSTOM_DEFAULT}
        raise gen.Return(teamname_custom)
