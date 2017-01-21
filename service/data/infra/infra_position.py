# coding=utf-8

from service.data.base import DataService
import tornado.gen as gen
from util.common import ObjectDict
from conf.path import POSITION_LIST
from util.tool.http_tool import http_get, http_post, http_put, http_delete, http_patch


class InfraPositionDataService(DataService):

    @gen.coroutine
    def get_position_list(self, params):
        ret = yield http_get(POSITION_LIST, params)
        raise gen.Return(ret)

