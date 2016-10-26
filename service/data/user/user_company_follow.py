# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.17

"""

from tornado import gen
from service.data.base import *
from util.common import ObjectDict


class UserCompanyFollowDataService(DataService):

    @gen.coroutine
    def get_user(self, conds, fields=[]):
        """
        Testing code and delete when release
        """
        if not self._valid_conds(conds):
            raise gen.Return(ObjectDict())
        if not fields:
            fields = self.user_company_follow_dao.fields_map.keys()
        response = yield self.user_company_follow_dao.get_record_by_conds(
                            conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def get_fllw_cmpy(self, conds, fields=[]):
        if not self._valid_conds(conds):
            raise gen.Return(ObjectDict())
        if not fields:
            fields = self.user_company_follow_dao.fields_map.keys()
        try:
            response = yield self.user_company_follow_dao.get_list_by_conds(
                                    conds, fields)
        except Exception as error:
            self.logger.warn(error)
            raise gen.Return(ObjectDict())

        raise gen.Return(response)

    @gen.coroutine
    def update_fllw_cmpy(self, conds, fields):
        try:
            response = self.user_company_follow_dao.update_by_conds(
                            conds, fields)
        except Exception as error:
            self.logger(error)
            raise gen.Return(False)

        raise gen.Return(response)

    @gen.coroutine
    def create_fllw_cmpy(self, fields):
        try:
            response = self.user_company_follow_dao.insert_record(fields)
        except Exception as error:
            self.logger(error)
            raise gen.Return(None)

        raise gen.Return(response)
