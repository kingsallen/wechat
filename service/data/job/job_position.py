# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict
from util.tool.http_tool import http_get


class JobPositionDataService(DataService):

    @gen.coroutine
    def get_position(self, conds, fields=[]):

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn("Warning:[get_position][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.job_position_dao.fields_map.keys())

        response = yield self.job_position_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    @cache(ttl=60)
    @gen.coroutine
    def get_positions_list(self, conds, fields=None, options=[], appends=[], index='', params=[]):

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn("Warning:[get_positions_list][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.job_position_dao.fields_map.keys())

        response = yield self.job_position_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)

    @gen.coroutine
    def update_position(self, conds=None, fields=None):
        if not conds or not fields:
            self.logger.warn(
                "Warning:[update_position][invalid parameters], Detail:[conds: {0}, fields: {1}]".format(
                    conds, fields))
            raise gen.Return(None)

        ret = yield self.job_position_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_positions(self, position_id):
        """获得 JD 页推荐职位
        reference: https://wiki.moseeker.com/position-api.md#recommended

        :param position_id: 职位 id
        """

        req = ObjectDict({
            'pid': position_id,
        })
        try:
            response = list()
            ret = yield http_get(self.path.POSITION_RECOMMEND, req)
            if ret.status == 0:
                response = ret.data
        except Exception as error:
            self.logger.warn(error)

        raise gen.Return(response)
