# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import *

class WxUserCompanyDataService(DataService):

    @gen.coroutine
    def get_user(self, conds, fields=[]):
        if not self._condition_isvalid(conds, 'get_user'):
            raise gen.Return(False)
        if not fields:
            fields = self.user_company_follows_dao.fields_map.keys()
        response = yield self.user_company_follows_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    def get_foll_cmpy_id_list(self, conds, fields):
        if not self._condition_isvalid(conds, 'get_foll_cmpy'):
            raise gen.Return(False)
        response = yield self.user_company_follows_dao.get_list_by_conds(conds, fields)
        raise gen.Return(response)
