# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrCompanyConfDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_company_conf(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_company_conf][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_company_conf_dao.fields_map.keys())

        response = yield self.hr_company_conf_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

