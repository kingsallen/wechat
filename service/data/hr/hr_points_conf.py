# coding=utf-8

# @Time    : 10/28/16 10:08
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_points_conf.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrPointsConfDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_points_conf(self, conds, fields=None, options=None, appends=None):

        fields = fields or []
        options = options or []
        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn("Warning:[get_points_conf][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_points_conf_dao.fields_map.keys())

        response = yield self.hr_points_conf_dao.get_record_by_conds(conds, fields, options, appends)
        raise gen.Return(response)
