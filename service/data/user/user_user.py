# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class UserUserDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_user(self, conds, fields=None):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_user][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(False)

        if not fields:
            fields = self.user_user_dao.fields_map.keys()

        response = yield self.user_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

