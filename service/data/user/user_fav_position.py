# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class UserFavPositionDataService(DataService):
    @cache(ttl=60)
    @gen.coroutine
    def get_user_fav_position(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_user_fav_position][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.user_fav_position_dao.fields_map.keys())

        response = yield self.user_fav_position_dao.get_record_by_conds(
            conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_user_fav_position_list(self, conds, fields=None, options=None,
                                   appends=None, index='', params=None):
        options = options or []
        appends = appends or []
        params = params or []

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_hr_hb_position_binding_list][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.user_fav_position_dao.fields_map.keys())

        response = yield self.user_fav_position_dao.get_list_by_conds(
            conds, fields, options, appends, index, params)

        raise gen.Return(response)

    @gen.coroutine
    def insert_user_fav_position(self, fields, options=None):
        options = options or []

        response = yield self.user_fav_position_dao.insert_record(
            fields, options)

        raise gen.Return(response)

    @gen.coroutine
    def update_user_fav_position(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warn("Warning:[update_user_fav_position][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(conds, fields))
            raise gen.Return(False)

        ret = yield self.user_fav_position_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)
