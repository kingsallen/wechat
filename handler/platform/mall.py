# coding=utf-8

from tornado.httputil import url_concat
from tornado import gen

import conf.common as const
import conf.message as msg
import conf.fe as fe
import conf.message as messages
import conf.path as path
from handler.base import BaseHandler
from handler.platform.user import UserSurveyConstantMixin
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str
from urllib import parse
import conf.platform as const_platform
from util.wechat.core import get_temporary_qrcode


class MallIndexHandler(BaseHandler):
    """Render page to /mall/goods_list.html
    包含： 商城是否开通， 剩余积分
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id

        # 商城状态：是否开通
        result_state, data_state = yield self.mall_ps.get_mall_state(company_id)
        state = data_state.get('state') if result_state else 0

        result_credit, data_credit = yield self.mall_ps.get_employee_left_credit(employee_id)
        left_credit = data_credit.get('award') if result_credit else 0

        self.render_page(
            template_name="mall/goods_list.html",
            data={
                "remain_credit": left_credit,
                "mall_state": state,
            },
            meta_title='积分商城'
        )


class MallGoodsHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
         分页获取商品列表
        |字段名|类型|说明|
        |--|--|--|
        |page_number|int|1: 第几页|
        |page_size|int|10: 每一页多少条商品数据|

        - path: /api/mall/goods
        - method: GET
        - params:
          ```
          {
             "page_number": 1,
             "page_size": 10
          }
          ```
        - return:
          ```
            {
              "status": 0,
              "message": "success",
              "data": {
                    list: [
                        {
                            id: 1,//商品编号
                            pic_url: "",//商品展示图url
                            title: "",//商品名称
                            credit: 1999,//兑换积分
                            stock: 99,//库存
                            exchange_order: 99,//兑换量（订单数）
                        }，{
                         ...
                      },...
                    ],
                    total_row: 22
                }
            }
          ```
        """
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id

        self.params.share = yield self._make_share()

        page_size = int(self.get_argument("page_size", "") or 10)
        page_number = int(self.get_argument("page_number", "") or 1)
        result, data = yield self.mall_ps.get_goods_list(employee_id, company_id, page_size, page_number)

        if result:
            self.send_json_success(data=data)
        else:
            self.send_json_error()

    @gen.coroutine
    def _make_share(self):
        link = self.make_url(
            path.EMPLOYEE_MALL,
            self.params)
        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = self.locale.translate(msg.CREDIT_MALL_SHARE_TITLE.format(company_info.abbreviation))
        description = self.locale.translate(msg.CREDIT_MALL_SHARE_TEXT)

        share_info = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })
        self.logger.info('Share_info: %s' % share_info)
        return share_info


