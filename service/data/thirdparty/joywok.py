# coding=utf-8


import tornado.gen as gen

import conf.common as const
import conf.path as path
import conf.alphacloud_api as api
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing, http_get_rp
from util.common.decorator import log_core
from setting import settings


class JoywokDataService(DataService):

    @gen.coroutine
    def get_joywok_info(self, params, headers=None):
        ret = yield http_get(path.JOYWOK_JMIS_AUTH, jdata=params, infra=False, headers=headers)
        return ret
