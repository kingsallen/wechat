# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import check_sub_company, handle_response
from util.tool.str_tool import add_item

class CompanyHandler(BaseHandler):
    """公司详情页新样式"""

    @handle_response
    @check_sub_company
    @gen.coroutine
    def get(self, did):

        company_info = yield self.company_ps.get_company(
            conds={"id": did}, need_conf=True)

        data = yield self.user_company_ps.get_company_data(
            self.params, company_info, self.current_user)

        share = self._share(company_info)

        company = ObjectDict(
            id=company_info.id,
            logo=self.static_url(company_info.logo),
            name=company_info.name,
            abbreviation=company_info.abbreviation,
            description=company_info.introduction,
        )

        self.send_json_success(data={
            "company": company,
            "templates": data.templates,
            "share": share,
            "cover": "aaa"
        })

    def _share(self, company):
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            'cover': self.static_url(company.get('logo', '')),
            'title': '关于{}, 你想知道的都在这里'.format(company_name),
            'description': '这可能是你人生的下一站! 看清企业全局, 然后定位自己',
            'link': self.fullurl()
        })

        return default
