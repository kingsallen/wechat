# coding=utf-8


import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get


class JoywokDataService(DataService):

    @gen.coroutine
    def get_joywok_info(self, params, headers=None):
        ret = yield http_get(path.JOYWOK_JMIS_AUTH, jdata=params, infra=False, headers=headers)
        return ret
