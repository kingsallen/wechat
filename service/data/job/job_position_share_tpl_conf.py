# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class JobPositionShareTplConfDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_share_conf(self, conds, fields=None):
        fields = fields or []

        if conds is None or not (isinstance(conds, dict) or isinstance(conds, str)):
            self.logger.warn("Warning:[get_share_conf][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(None)

        if not fields:
            fields = list(self.job_position_share_tpl_conf_dao.fields_map.keys())

        response = yield self.job_position_share_tpl_conf_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)
