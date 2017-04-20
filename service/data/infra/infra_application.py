# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get, http_post, http_put


class InfraApplicationDataService(DataService):

    """对接申请服务
        referer: https://wiki.moseeker.com/application-api.md"""

    @gen.coroutine
    def get_application_apply_count(self, params):
        """获取一个月内该用户再该用户的申请数量
        """
        ret = yield http_post(path.INFRA_APPLICATION_APPLY_COUNT, params)
        raise gen.Return(ret)

    @gen.coroutine
    def create_application(self, params):
        """创建申请
        """
        ret = yield http_post(path.INFRA_APPLICATION, params)
        raise gen.Return(ret)

    @gen.coroutine
    def update_application(self, params):
        """更新申请
        """
        ret = yield http_put(path.INFRA_APPLICATION, params)
        raise gen.Return(ret)
