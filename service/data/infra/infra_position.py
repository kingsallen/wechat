# coding=utf-8

from service.data.base import DataService
import tornado.gen as gen
import conf.path as path
from util.tool.http_tool import http_get


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
