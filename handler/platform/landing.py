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
            "city": self.params.city,
            "salary": self.params.salary,
            "occupation": self.params.occupation,
            "department": self.params.department,
            "candidate_source": self.params.candidate_source,
            "employment_type": self.params.employment_type,
            "degree": self.params.degree,
            "did": int(self.params.did) if self.params.did else 0,
            "custom": self.params.custom
        })

        search_seq = yield self.landing_ps.get_landing_item(self.current_user.company,
                                                            self.current_user.wechat.company_id, selected)

        company = ObjectDict({
            "logo": self.static_url(self.current_user.company.logo),
            "name": self.current_user.company.get("abbreviation"),
            "image": self.static_url(self.current_user.company.conf_search_img),
            "search_seq": search_seq
        })

        self.render(template_name="company/search.html", company=company)
