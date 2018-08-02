# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing
from util.common.decorator import log_time


class InfraEmployeeDataService(DataService):
    """对接内推服务"""

    @gen.coroutine
    def get_referral_policy(self, company_id):
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield http_get(path.REFERRAL_POLICY, params)
        return unboxing(ret)

    @gen.coroutine
    def create_interest_policy_count(self, params):
        ret = yield http_post(path.INTEREST_REFERRAL_POLICY, params)
        return unboxing(ret)


