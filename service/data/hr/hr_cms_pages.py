# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2016.11.22

"""

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrCmsPagesDataService(DataService):
    # @cache(ttl=300)
    @gen.coroutine
    def get_page(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_medium][invalid parameters], \
                        Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_cms_pages_dao.fields_map.keys())

        response = yield self.hr_cms_pages_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
