# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.17

"""

from tornado import gen
from service.data.base import *
from util.common import ObjectDict


class UserCompanyVisitReqDataService(DataService):

    @gen.coroutine
    def get_visit_cmpy(self, conds, fields=[]):
        if not self._valid_conds(conds):
            raise gen.Return(ObjectDict())
        if not fields:
            fields = self.user_company_visit_req_dao.fields_map.keys()
        try:
            response = yield self.user_company_visit_req_dao.get_list_by_conds(
                conds, fields)
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(ObjectDict())

        raise gen.Return(response)

    @gen.coroutine
    def update_visit_cmpy(self, conds, fields):
        try:
            response = self.user_company_visit_req_dao.update_by_conds(
                            conds, fields)
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(False)

        raise gen.Return(response)

    @gen.coroutine
    def create_visit_cmpy(self, fields):
        try:
            response = yield self.user_company_visit_req_dao.insert_record(fields)
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(None)

        raise gen.Return(response)
