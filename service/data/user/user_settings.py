# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class UserSettingsDataService(DataService):

    @gen.coroutine
    def create_user_settings(self, fields, options=None):
        options = options or []

        response = yield self.user_settings_dao.insert_record(fields, options)
        raise gen.Return(response)
