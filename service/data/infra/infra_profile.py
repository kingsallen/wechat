# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post


class InfraProfileDataService(DataService):

    """对接profile服务
        referer: https://wiki.moseeker.com/profile-api.md"""

    @gen.coroutine
    def has_profile(self, user_id):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param user_id:
        :param from_hr: 是否模拟hr端调用接口
        :return: tuple (bool, profile or None)

        调用方式:
        profile = has_profile[1]
        """
        params = ObjectDict(user_id=user_id)
        res = yield http_get(path.INFRA_PROFILE, params)
        ret = "status" not in res
        raise gen.Return((ret, res))

    @gen.coroutine
    def get_application_apply_count(self, params):
        """获取一个月内该用户再该用户的申请数量
        """
        ret = yield http_post(path.INFRA_APPLICATION_APPLY_COUNT, params)
        raise gen.Return(ret)
