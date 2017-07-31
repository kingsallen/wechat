# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrGroupCompanyRelDataService(DataService):

    @cache(ttl=300)
    @gen.coroutine
    def get_hr_group_company_rel(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning(
                "Warning:[get_hr_group_company_rel][invalid parameters], Detail:[conds: {0}, type: {1}]"
                    .format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_group_company_rel_dao.fields_map.keys())

        response = yield self.hr_group_company_rel_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
