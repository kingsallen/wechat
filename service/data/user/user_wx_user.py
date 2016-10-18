# coding=utf-8

import time

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class UserWxUserDataService(DataService):

    @gen.coroutine
    def get_wxuser(self, id=None):
        if not id:
            self.logger.warn(u"Warning:[get_wxuser][invalid parameters], Detail:[id: {0}]".format(id))
            raise gen.Return(None)

        conds = {"id": [str(id), "="]}
        fields = self.user_wx_user_dao.fields_map.keys()

        response = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_wxuser(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warn(u"Warning:[get_wxuser][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(None)

        fields = fields or list(self.user_wx_user_dao.fields_map.keys())

        response = yield self.user_wx_user_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def create_wxuser(self, fields, options=None):
        options = options or []

        response = yield self.user_wx_user_dao.insert_record(fields, options)
        raise gen.Return(response)

    @gen.coroutine
    def update_wxuser(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warn(u"Warning:[update_wxuser][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(None)

        ret = yield self.user_wx_user_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)
