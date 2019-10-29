# coding=utf-8

from tornado import gen

import conf.message as msg
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common


class MallIndexHandler(BaseHandler):
    """Render page to /mall/goods_list.html
    包含： 商城是否开通， 剩余积分
    """

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id

        # 商城状态：是否开通
        result_state, data_state = yield self.mall_ps.get_mall_state(company_id)
        state = data_state.get('state') if result_state else 0

        result_credit, data_credit = yield self.mall_ps.get_employee_left_credit(employee_id)
        left_credit = data_credit.get('award') if result_credit else 0

        self.params.share = yield self._make_share()
        self.render_page(
            template_name="mall/goods_list.html",
            data={
                "remain_credit": left_credit,
                "mall_state": state,
            },
            meta_title='积分商城'
        )

    @gen.coroutine
    def _make_share(self):
        link = self.make_url(
            path.EMPLOYEE_MALL,
            self.params)
        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = msg.CREDIT_MALL_SHARE_TITLE.format(company_info.abbreviation)
        description = msg.CREDIT_MALL_SHARE_TEXT

        share_info = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })
        return share_info


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

        page_size = int(self.get_argument("page_size", "") or 0)
        page_number = int(self.get_argument("page_number", "") or 1)
        result, data = yield self.mall_ps.get_goods_list(employee_id, company_id, page_size, page_number)

        if result:
            self.send_json_success(data=data)
        else:
            self.send_json_error()


class MallGoodHandler(BaseHandler):

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self, good_id):
        """
        获取商品详情信息
        :return:
        """
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id

        result, data = yield self.mall_ps.get_good_detail(good_id, company_id)

        result_credit, data_credit = yield self.mall_ps.get_employee_left_credit(employee_id)
        remain_credit = data_credit.get('award') if result_credit else 0

        good_title = data.get('title')
        self.params.share = yield self._make_share(good_id, good_title)

        render_page_data = data
        render_page_data.update({
            "remain_credit": remain_credit
        }
        )
        self.render_page(
            template_name="mall/goods_info.html",
            data=render_page_data,
            meta_title='积分商城'
        )

    @gen.coroutine
    def _make_share(self, good_id, good_title):
        link = self.make_url(
            path.MALL_GOOD.format(good_id=good_id),
            self.params)
        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)
        title = msg.MALL_GOOD_DETAIL_SHARE_TITLE.format(good_title)
        description = msg.MALL_GOOD_DETAIL_SHARE_TEXT

        share_info = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })
        return share_info


class MallExchangeHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        获取兑换记录列表
        - path: /api/mall/order
        - params:
        - return:
          ```
            {
              "status": 0,
              "message": "success",
              "data": [
                  {
                    "id": 1,//订单号
                    "order_id": 1,//订单编号
                    "employee": "李童威",//兑换人姓名
                    "good_id": 123,//商品id
                    "credit": 123,//商品兑换积分
                    "name": "哈哈",//兑换人姓名
                    "mobile": 13833333333,//手机
                    "email": "litongwei@moseeker.com",//邮箱
                    "custom": "0001",//自定义
                    "title": "",//兑换商品名称
                    "pic_url": "",//兑换商品主图url
                    "count": 10,//数量
                    "order_state": 1,//0 已申请兑换未发放  1 已发放  2 不发放
                    "employee_state": 1,//0 已认证  1 未认证  2 已删除
                    "create_time": "2018-09-22 12:33:11"//兑换时间
                    "assign_time": "2018-09-22 12:33:11"//发放时间
                   },
                   {...}
                ]
            }
          ```
        """
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id

        result, data = yield self.mall_ps.exchange_list(employee_id, company_id)
        if result:
            self.send_json_success(data)
        else:
            self.send_json_error()

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        """
        立即兑换商品
        -path: /api/mall/order
        -params:
        {
            "count": 1, // 商品兑换数量
            "goods_id": 123  //商品id
        }
        :return: 当库存不足10038， 当前积分不足10039， 商品已下架10043是返回指定code

        """
        company_id = self.current_user.company.id
        employee_id = self.current_user.employee.id

        count = int(self.json_args.count)
        goods_id = int(self.json_args.goods_id)

        res = yield self.mall_ps.exchange_imd(employee_id, company_id, count, goods_id)

        #
        if res.status == 0:
            self.send_json_success()
        elif res.status in [10038, 10039, 10043]:
            self.send_json_warning(message=res.message, status_code=res.status)
        else:
            self.send_json_error()


class MallExchangePageHandler(BaseHandler):
    """Render page to /mall/order_list.html
    兑换记录页面
    """

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        company_id = self.current_user.company.id

        result_state, data_state = yield self.mall_ps.get_mall_state(company_id)
        state = data_state.get('state') if result_state else 0

        self.render_page(
            template_name="mall/order_list.html",
            data={
                "mall_state": state,
            },
            meta_title='积分商城'
        )
