# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.tool.http_tool import http_get
from util.common import ObjectDict


class InfraPositionDataService(DataService):
    """对接职位服务
        referer: https://wiki.moseeker.com/position-api.md"""

    @gen.coroutine
    def get_position_list(self, params):
        """普通职位列表"""
        ret = yield http_get(path.INFRA_POSITION_LIST, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_position_list_rp_ext(self, params):
        """获取职位的红包信息"""
        ret = yield http_get(path.INFRA_POSITION_LIST_RP_EXT, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_rp_position_list(self, params):
        """红包职位列表"""
        ret = yield http_get(path.INFRA_RP_POSITION_LIST, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_rp_share_info(self, params):
        """红包职位列表的分享信息"""
        ret = yield http_get(path.INFRA_RP_POSITION_LIST_SHARE_INFO, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_positions(self, position_id):
        """获得 JD 页推荐职位
        reference: https://wiki.moseeker.com/position-api.md#recommended

        :param position_id: 职位 id
        """

        req = ObjectDict({
            'pid': position_id,
        })
        try:
            response = list()
            ret = yield http_get(path.INFRA_POSITION_RECOMMEND, req)
            if ret.status == 0:
                response = ret.data
        except Exception as error:
            self.logger.warning(error)

        raise gen.Return(response)
