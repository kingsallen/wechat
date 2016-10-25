# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class UserFavPositionDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_user_fav_position(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warn("Warning:[get_user_fav_position][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = list(self.user_fav_position_dao.fields_map.keys())

        response = yield self.user_fav_position_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

