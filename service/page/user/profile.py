# coding=utf-8

import tornado.gen as gen

from service.page.base import PageService
import conf.common as const
import conf.path as path
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post


class ProfilePageService(PageService):
    """对接profile服务
    referer: https://wiki.moseeker.com/profile-api.md
    """

    @gen.coroutine
    def has_profile(self, user_id):
        """
        判断 user_user 是否有 profile (profile_profile 表数据)
        :param user_id:
        :return: tuple (bool, profile or None)

        调用方式:
        profile = has_profile[1]
        """

        response = yield self.profile_ds.get_profile(user_id)
        ret = bool(response.status == const.API_SUCCESS)
        profile = None
        if ret:
            profile = response.data
        return ret, profile


