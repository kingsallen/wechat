# coding=utf-8

import json

from tornado import gen
import time
import conf.common as const
import conf.fe as fe
import conf.message as msg
import conf.path as path
from service.page.base import PageService
from setting import settings
from thrift_gen.gen.employee.struct.ttypes import BindingParams, BindStatus
from util.common import ObjectDict
from util.tool.dict_tool import sub_dict
from util.tool.re_checker import revalidator
from util.tool.url_tool import make_static_url, make_url
from util.tool.str_tool import gen_salary, gen_experience_v2
from util.wechat.core import get_temporary_qrcode
from util.common.mq import unread_praise_publisher


class MallPageService(PageService):
    # 积分商城服务

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_mall_state(self, company_id):
        """获取商城状态：0 未开启 1 开启 2 已开启现在是停用状态
        """
        result, data = yield self.infra_mall_ds.get_mall_state(
            company_id
        )
        return result, data

    @gen.coroutine
    def get_employee_left_credit(self, employee_id):
        """获取员工剩余积分"""
        result, data = yield self.infra_mall_ds.get_left_credit(employee_id)
        return result, data

    @gen.coroutine
    def get_goods_list(self, employee_id, company_id, page_size, page_number):
        """获取商品列表"""
        result, data = yield self.infra_mall_ds.get_goods_list(employee_id, company_id, page_size, page_number)
        return result, data

    @gen.coroutine
    def get_good_detail(self, good_id, company_id):
        """获取商品详情"""
        result, data = yield self.infra_mall_ds.get_good_detail(good_id, company_id)
        return result, data

    @gen.coroutine
    def exchange_imd(self, employee_id, company_id, count, goods_id, name, mobile, province, city, region, address, user_id):
        """立即兑换商品"""
        res = yield self.infra_mall_ds.exchange_imd(employee_id, company_id, count, goods_id, name, mobile, province, city, region, address, user_id)
        return res

    @gen.coroutine
    def exchange_list(self, employee_id, company_id):
        """获取兑换记录列表"""
        result, data = yield self.infra_mall_ds.exchange_list(employee_id, company_id)
        return result, data
