# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from conf.newinfra_service_conf.referral import redpacket
from conf.newinfra_service_conf.service_info import redpacket_service
from util.tool.http_tool import http_get_v2, http_post_v2


class InfraRedpacketDataService(DataService):

    @gen.coroutine
    def infra_get_redpacket_info(self, params):
        ret = yield http_get_v2(redpacket.CLOUD_REDPACKET_SCENE, redpacket_service, params)
        return ret

    @gen.coroutine
    def infra_open_redpacket(self, params):
        ret = yield http_post_v2(redpacket.CLOUD_REDPACKET_CLAIM, redpacket_service, params)
        return ret

    @gen.coroutine
    def infra_get_rp_position_share_info(self, params):
        ret = yield http_get_v2(redpacket.CLOUD_RP_POSITION_SHARE_INFO, redpacket_service, params)
        return ret

    @gen.coroutine
    def get_redpacket_list(self, params):
        res = yield http_get_v2(redpacket.CLOUD_USER_REDPACKET_LIST, redpacket_service, params)
        return res
