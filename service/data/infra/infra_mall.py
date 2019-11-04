# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing, http_delete, http_post_multipart_form
from requests.models import Request
from setting import settings
from globals import env


class InfraMallDataService(DataService):
    """积分商城服务"""

    @gen.coroutine
    def get_mall_state(self, company_id):
        """
         获取积分商城开关状态
        :param company_id:
        :return:

        """
        params = ObjectDict({
            "company_id": company_id,
        })
        ret = yield http_get(path.MALL_SWITCH, params)
        return unboxing(ret)

    @gen.coroutine
    def get_left_credit(self, employee_id):
        ret = yield http_get(path.LEFT_CREDIT.format(employee_id))
        return unboxing(ret)

    @gen.coroutine
    def get_goods_list(self, employee_id, company_id, page_size, page_number):
        params = ObjectDict({
            "company_id": company_id,
            "employee_id": employee_id,
            "page_size": page_size,
            "page_number": page_number
        })
        ret = yield http_get(path.GOODS_LIST, params)
        return unboxing(ret)

    @gen.coroutine
    def get_good_detail(self, good_id, company_id):
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield http_get(path.GOOD_DETAIL.format(good_id=good_id), params)

        return unboxing(ret)

    @gen.coroutine
    def exchange_imd(self, params):
        ret = yield http_post(path.EXCHANGE, params)
        return ret

    @gen.coroutine
    def exchange_list(self, employee_id, company_id):
        params = ObjectDict({
            "employee_id": employee_id,
            "company_id": company_id,
        })
        ret = yield http_get(path.EXCHANGE, params)

        return unboxing(ret)
