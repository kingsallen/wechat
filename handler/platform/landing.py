# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen

from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response


class LandingHandler(BaseHandler):
    """
    企业搜索页
    """

    @handle_response
    @gen.coroutine
    def get(self):
        selected = ObjectDict({
            "city": self.get_argument("city", ''),
            "salary": self.get_argument("salary", ''),
            "occupation": self.get_argument("occupation", ''),
            "department": self.get_argument("department", ''),
            "candidate_source": self.get_argument("candidate_source", ''),
            "employment_type": self.get_argument("employment_type", ''),
            "degree": self.get_argument("degree", ''),
            "did": int(self.get_argument("did", 0)) if self.get_argument("did", 0) else 0,
            "custom": self.get_argument("custom", '')
        })

        search_seq = yield self.landing_ps.get_landing_item(self.current_user.company,
                                                            self.current_user.wechat.company_id, selected)

        company = ObjectDict({
            "logo": self.static_url(self.current_user.company.get("logo")),
            "name": self.current_user.company.get("abbreviation"),
            "image": self.static_url(self.current_user.company.get("conf_search_img")),
            "search_seq": search_seq
        })

        self.render(template_name="company/search.html", company=company)
