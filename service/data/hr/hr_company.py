# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrCompanyDataService(DataService):

    @cache(ttl=300)
    @gen.coroutine
    def get_company(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_company][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_company_dao.fields_map.keys())

        response = yield self.hr_company_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=300)
    @gen.coroutine
    def get_companys_list(self, conds, fields, options=None, appends=None, index='', params=None):

        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_companys_list][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_company_dao.fields_map.keys())

        response = yield self.hr_company_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)

    @gen.coroutine
    def create_company(self, fields, options=None):

        options = options or []

        response = yield self.hr_company_dao.insert_record(fields, options)
        raise gen.Return(response)

    @gen.coroutine
    def update_company(self, conds=None, fields=None):

        if not conds or not fields:
            self.logger.warning("Warning:[update_company][invalid parameters], "
                                "Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(False)

        ret = yield self.hr_company_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)
