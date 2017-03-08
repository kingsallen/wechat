# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get, unboxing, http_post


class InfraCompanyDataService(DataService):

    @gen.coroutine
    def get_company_all(self, params):
        res = yield http_get(path.COMPANY_ALL, params)
        return unboxing(res)

    @gen.coroutine
    def create_company_on_wechat(self, params) -> list:
        res = yield http_post(path.COMPANY, params)
        return res
