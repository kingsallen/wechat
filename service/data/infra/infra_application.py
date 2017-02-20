# coding=utf-8

from service.data.base import DataService
import tornado.gen as gen
import conf.path as path
from util.tool.http_tool import http_get, http_post


class InfraApplicationDataService(DataService):

    """对接申请服务
        referer: https://wiki.moseeker.com/application-api.md"""

    @gen.coroutine
    def get_application_apply_count(self, params):
        """获取一个月内该用户再该用户的申请数量
        """
        ret = yield http_post(path.INFRA_APPLICATION_APPLY_COUNT, params)
        raise gen.Return(ret)