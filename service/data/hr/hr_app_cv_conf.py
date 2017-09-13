# coding=utf-8


from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrAppCvConfDataService(DataService):

    #@cache(ttl=60)
    @gen.coroutine
    def get_app_cv_conf(self, conds, fields=None, options=None, appends=None):

        fields = fields or []
        options = options or []
        appends = appends or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn(
                "Warning:[get_app_cv_conf][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            return ObjectDict()

        if not fields:
            fields = list(self.hr_app_cv_conf_dao.fields_map.keys())

        response = yield self.hr_app_cv_conf_dao.get_record_by_conds(
            conds, fields, options, appends)
        return response
