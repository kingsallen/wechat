# coding=utf-8

import tornado.gen as gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
from util.common.decorator import log_coro


class RedpacketPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_redpacket_info(self, id, cardno, user_id):
        """获取红包信息"""
        ret = yield self.infra_redpacket_ds.infra_get_redpacket_info({
            "id": id,
            "cardno": cardno,
            "user_id": user_id
        })
        return ret

    @gen.coroutine
    def get_redpacket_list(self, params):
        """获取红包列表"""
        ret = yield self.infra_redpacket_ds.get_redpacket_list(params)
        if int(ret.code) == const.API_SUCCESS:
            data = ret.data
        else:
            data = ObjectDict()
        return data

    @gen.coroutine
    def open_redpacket(self, id, cardno, user_id):
        """领取红包"""
        ret = yield self.infra_redpacket_ds.infra_open_redpacket({
            "id": id,
            "cardno": cardno,
            "user_id": user_id
        })
        return ret

    @log_coro
    @gen.coroutine
    def get_last_running_hongbao_config_by_position(self, position_id):
        """
        获取一个职位正在进行的红包活动
        """

        share_info = yield self.infra_redpacket_ds.infra_get_rp_position_share_info(
            {
                "positionId": position_id
            }
        )
        raise gen.Return(share_info.data)
