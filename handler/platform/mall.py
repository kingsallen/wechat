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
        result_state, data_state = yield self.mall_ps.get_mall_state(company_id, employee_id)
        state = data_state.get('state') if result_state else 0

        result_credit, data_credit = yield self.mall_ps.get_employee_left_credit(employee_id)
        left_credit = data_credit.get('award') if result_credit else 0

        self.render_page(template_name="mall/goods_list.html",
                         data={
                             "remain_credit": left_credit,
                             "mall_state": state
                         })
