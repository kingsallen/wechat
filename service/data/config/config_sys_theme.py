# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class ConfigSysThemeDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_theme(self, conds, fields=None):

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_theme][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.config_sys_theme_dao.fields_map.keys())

        response = yield self.config_sys_theme_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
