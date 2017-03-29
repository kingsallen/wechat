# -*- coding=utf-8 -*-
# Copyright 2017 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2017.03.26
"""

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrCmsModuleDataService(DataService):
    # @cache(ttl=300)
    @gen.coroutine
    def get_module(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_module][invalid parameters], \
                        Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_cms_module_dao.fields_map.keys())

        response = yield self.hr_cms_module_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    # @cache(ttl=300)
    @gen.coroutine
    def get_module_list(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_module_list][invalid parameters], \
                        Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_cms_module_dao.fields_map.keys())

        response = yield self.hr_cms_module_dao.get_list_by_conds(conds, fields)
        raise gen.Return(response)
