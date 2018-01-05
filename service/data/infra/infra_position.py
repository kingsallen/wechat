# coding=utf-8

import tornado.gen as gen
from tornado.testing import AsyncTestCase, gen_test

import conf.path as path
from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.position.service.PositionServices import Client as PositionServiceClient
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post


class InfraPositionDataService(DataService):
    """对接职位服务
        referer: https://wiki.moseeker.com/position-api.md"""

    @gen.coroutine
    def get_position_list(self, params):
        """普通职位列表"""
        ret = yield http_get(path.INFRA_POSITION_LIST, params)
        return ret

    @gen.coroutine
    def get_position_list_rp_ext(self, params):
        """获取职位的红包信息"""
        ret = yield http_get(path.INFRA_POSITION_LIST_RP_EXT, params)
        return ret

    @gen.coroutine
    def get_rp_position_list(self, params):
        """红包职位列表"""
        ret = yield http_get(path.INFRA_RP_POSITION_LIST, params)
        return ret

    @gen.coroutine
    def get_rp_share_info(self, params):
        """红包职位列表的分享信息"""
        ret = yield http_get(path.INFRA_RP_POSITION_LIST_SHARE_INFO, params)
        return ret

    @gen.coroutine
    def get_sug_list(self, params):
        ret = yield http_post(path.INFRA_SUG_LIST, params)
        return ret

    @gen.coroutine
    def get_position_personarecom(self, params):
        """获取推荐职位列表接口（ai项目第二期）"""
        ret = yield http_get(path.INFRA_POSITION_PERSONARECOM, params)
        return ret

    @gen.coroutine
    def get_position_employeerecom(self, params):
        """获取推荐职位列表接口（ai项目第四期）"""
        ret = yield http_get(path.INFRA_POSITION_EMPLOYEERECOM, params)
        return ret

    @gen.coroutine
    def get_recommend_positions(self, position_id):
        """获得 JD 页推荐职位
        reference: https://wiki.moseeker.com/position-api.md#recommended

        :param position_id: 职位 id
        """

        req = ObjectDict({
            'pid': position_id,
        })
        response = list()
        try:
            ret = yield http_get(path.INFRA_POSITION_RECOMMEND, req)
            if ret.status == 0:
                response = ret.data
        except Exception as error:
            self.logger.warning(error)

        return response

    @gen.coroutine
    def get_third_party_synced_positions(self, company_id):
        """
        :param company_id: int, 公司id
        :return: list, position数据
        """
        req = ObjectDict({
            "companyId": company_id,
            "candidatesource": 1
        })
        response = {}
        try:
            ret = yield http_get(path.INFRA_THIRD_PARTY_SYNCED_POSITIONS, req)
            if ret.status == 0:
                response = ret.data or {}
        except Exception as error:
            self.logger.warning(error)

        return response


class TestEmployeeService(AsyncTestCase):
    """Just for test(or try results) during development :)"""

    def setUp(self):
        super().setUp()
        self.service = ServiceClientFactory.get_service(
            PositionServiceClient)

    @gen_test
    def testPositionList(self):
        ret = yield self.service.getPositionList()
        print(ret)
