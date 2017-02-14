# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class UserHrAccountDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_hr_account(self, conds, fields=None):

        if not self._valid_conds(conds):
            self.logger.warning("Warning:[get_hr_account][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.user_hr_account_dao.fields_map.keys())

        response = yield self.user_hr_account_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @gen.coroutine
    def update_hr_account(self, conds, fields):
        try:
            response = yield self.user_hr_account_dao.update_by_conds(
                conds=conds, fields=fields
            )
        except Exception as error:
            self.logger.warning(error)
            raise gen.Return(False)

        raise gen.Return(response)

