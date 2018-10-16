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
    def get_mall_state(self, company_id, employee_id):
        """
         获取积分商城开关状态
        :param company_id:
        :param employee_id:
        :return:

        """
        params = ObjectDict({
            "company_id": company_id,
            "employee_id": employee_id
        })
        ret = yield http_get(path.MALL_SWITCH, params)
        return unboxing(ret)

    @gen.coroutine
    def get_left_credit(self, employee_id):
        ret = yield http_get(path.LEFT_CREDIT.format(employee_id))
        return unboxing(ret)
