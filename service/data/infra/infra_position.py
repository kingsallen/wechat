# coding=utf-8

import tornado.gen as gen
from tornado.testing import AsyncTestCase, gen_test

import conf.path as path
import conf.alphacloud_api as api
from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.position.service.PositionServices import Client as PositionServiceClient
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_patch, http_get_rp, http_get_v2, http_post_v2
from util.tool import http_tool
from util.common.decorator import cache_new
from conf.newinfra_service_conf.service_info import position_service
from conf.newinfra_service_conf.position import position


class InfraPositionDataService(DataService):
    """对接职位服务
        referer: https://wiki.moseeker.com/position-api.md"""

    @cache_new(ttl=300, escape=['user_id'])
    @gen.coroutine
    def get_position_list(self, params):
        """普通职位列表"""
        ret = yield http_post_v2(position.POSITION_LIST, position_service, params, timeout=7)
        return ret

    @gen.coroutine
    def get_position_list_rp_ext(self, params):
        """获取职位的红包信息"""
        ret = yield http_get_rp(api.redpacket_service.api.CLOUD_POSITION_LIST_RP_EXT, api.redpacket_service.service, params)
        return ret

    @gen.coroutine
    def get_rp_position_list(self, params):
        """红包职位列表"""
        ret = yield http_get(path.INFRA_RP_POSITION_LIST, params)
        return ret

    @gen.coroutine
    def get_rp_share_info(self, params):
        """红包职位列表的分享信息"""
        ret = yield http_get_rp(api.redpacket_service.api.CLOUD_RP_POSITION_LIST_SHARE_INFO, api.redpacket_service.service, params)
        return ret

    @gen.coroutine
    def get_position_bonus(self, pid):
        """获取职位奖金"""
        params = ObjectDict({
            "position_id": pid
        })
        ret = yield http_get(path.INFRA_POSITION_BONUS, params)
        return ret

    @gen.coroutine
    def post_sug_list(self, params):
        ret = yield http_post(path.INFRA_SUG_LIST, params)
        return http_tool.unboxing(ret)

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

    @gen.coroutine
    def get_position_feature(self, position_id):
        """
        :param position_id:
        :return:
        """
        ret = yield http_get(path.INFRA_POSITION_FEATURE.format(position_id))
        return http_tool.unboxing(ret)

    @gen.coroutine
    def get_recom_position_list_wx_tpl_receive(self, user_id, wechat_id):
        res = yield http_get(
            path.INFRA_POSITION_LATEST_REFUSAL_RECOM,
            dict(
                user_id=user_id,
                wechat_id=wechat_id
            ))
        return res

    @gen.coroutine
    def post_not_receive_recom_position_wx_tpl(self, user_id, wechat_id):
        res = yield http_post(
            path.INFRA_POSITION_LIST_WX_TPL,
            dict(
                user_id=user_id,
                wechat_id=wechat_id
            ))
        return res

    @gen.coroutine
    def get_position_search_history(self, user_id, app_id):
        res = yield http_get(
            path.INFRA_POSITION_SEARCH_HISTORY,
            dict(
                user_id=user_id,
                app_id=app_id,
            ))
        return res

    @gen.coroutine
    def patch_position_search_history(self, user_id, app_id):
        res = yield http_patch(
            path.INFRA_POSITION_SEARCH_HISTORY_DEL,
            dict(
                user_id=user_id,
                app_id=app_id
            ))
        return res

    @gen.coroutine
    def get_position_required_fields(self, position_id):
        """
        推荐关键信息-简历字段必填项数据获取
        :param position_id:
        :return:
        """
        res = yield http_get(
            path.INFRA_POSITION_REQUIRED_FIELDS,
            dict(
                position_id=position_id
            )
        )
        return res

    @gen.coroutine
    def insert_neo4j_share_record(self, recom_user_id, presentee_user_id, share_chain_id):
        """
        职位转发被点击时 neo4j记录转发链路
        :param recom_user_id:
        :param presentee_user_id:
        :param share_chain_id:
        :return:
        """
        params = {
            "start_user_id": recom_user_id,
            "end_user_id": presentee_user_id,
            "share_chain_id": share_chain_id
        }
        ret = yield http_post(path.INFRA_POSITION_NEO4J_SHARE_CHAIN, params)
        return ret

    @gen.coroutine
    def send_ten_min_tmp(self, user_id, company_id):
        """
        十分钟消息模板，改为基础服务发
        :param user_id: 员工user_id
        :param company_id:
        :return:
        """
        params = {
            "user_id": user_id,
            "company_id": company_id
        }
        ret = yield http_post(path.INFRA_TEN_MIN_TMP, params)
        return ret


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
