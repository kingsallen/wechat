# coding=utf-8

from tornado import gen

from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated


class GroupCompanyCheckHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """ 返回当前公司的集团公司相关信息
        https://git.moseeker.com/doc/hr/hr354docs/blob/master/wechat-fe.md"""
        need_list = False or bool(self.params.list)

        company_id = self.current_user.company.id

        result = ObjectDict()
        result.belongs_to_group = yield \
            self.company_ps.belongs_to_group_company(company_id)

        if need_list and result.belongs_to_group:
            result.company_list = \
                yield self.company_ps.get_group_company_list(company_id)

        self.send_json_success(data=result)

