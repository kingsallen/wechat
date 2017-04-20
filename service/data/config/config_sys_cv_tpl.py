# encoding=utf-8

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class ConfigSysCvTplDataService(DataService):

    @cache(ttl=60)
    @gen.coroutine
    def get_config_sys_cv_tpls(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warn(
                "Warning:[get_config_sys_cv_tpls][invalid parameters], "
                "Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            return ObjectDict()

        if not fields:
            fields = list(self.config_sys_cv_tpl_dao.fields_map.keys())

        response = yield self.config_sys_cv_tpl_dao.get_list_by_conds(conds, fields)
        return response
