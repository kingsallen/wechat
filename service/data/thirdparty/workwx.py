# coding=utf-8


import tornado.gen as gen
import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get, http_post_v2, http_get_v2
from conf.newinfra_service_conf.user import user
from conf.newinfra_service_conf.service_info import user_service


class WorkWXDataService(DataService):

    @gen.coroutine
    def create_workwx_user(self, params):
        ret = yield http_post_v2(user.INFRA_USER_WORKWX_USER, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_workwx_user(self, params):
        ret = yield http_get_v2(user.INFRA_USER_WORKWX_USER, user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_workwx(self, params):
        ret = yield http_get(path.COMPANY_GET_WORKWX, jdata=params)
        raise gen.Return(ret)
