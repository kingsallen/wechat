# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get, http_post, http_put, unboxing


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
    def get_application_apply_status(self, params):
        """
        获取求职者该公司社招社招职位是否达到投递上限
        """
        ret = yield http_post(path.INFRA_APPLICATION_TYPE_APPLY_COUNT, params)
        return unboxing(ret)

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

    @gen.coroutine
    def custom_cv_check_v2(self, params):
        """基础服务检查改用户的简历是否符合职位的自定义简历要求"""
        ret = yield http_post(path.PROFILE_CUSTOMCV_CHECK, params)
        return unboxing(ret)

    @gen.coroutine
    def bind_apply_chain_info(self, params):
        """
        将apply与链路其他信息（psc、直接推荐人）绑定
        :param params:
        :return:
        """
        ret = yield http_post(path.INFRA_BIND_APPLY_ID_AND_PSC, params)
        return unboxing(ret)
