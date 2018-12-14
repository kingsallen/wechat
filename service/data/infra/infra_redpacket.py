# coding=utf-8

import tornado.gen as gen
import conf.common as const

import conf.path as path
import util.tool.http_tool as http_tool
from service.data.base import DataService
import conf.alphacloud_api as api
from util.common import ObjectDict
from setting import settings


class InfraRedpacketDataService(DataService):

    @gen.coroutine
    def infra_get_redpacket_info(self, params):
        ret = yield http_tool.http_get_rp(api.redpacket_service.api.CLOUD_REDPACKET_SCENE, api.redpacket_service.service, params)
        return ret

    @gen.coroutine
    def infra_open_redpacket(self, params):
        ret = yield http_tool.http_post_rp(api.redpacket_service.api.CLOUD_REDPACKET_CLAIM, api.redpacket_service.service, params)
        return ret

