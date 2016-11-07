# coding=utf-8

# Copyright 2016 MoSeeker

from util.common import ObjectDict
from tornado import gen
# from handler.base import BaseHandler
from util.common.decorator import handle_response, url_valid
from handler.platform._base import BaseHandler


class LandingHandler(BaseHandler):

    """
    企业搜索页
    """
    
    def initialize(self, event):
        # 日志需要，由 route 定义
        self._event = event

    @url_valid
    @handle_response
    @gen.coroutine
    def get(self):
        signature = str(self.get_argument("wechat_signature", ""))
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

        if signature:
            conds = {'signature': signature}
            wechat = yield self.wechat_ps.get_wechat(conds)
            company_id = wechat.get("company_id")
        else:
            self.write_error(404)
            return

        search_seq = yield self.landing_ps.get_landing_item(self.current_user.company, company_id, selected)

        company = ObjectDict({
            "logo": self.static_url(self.current_user.company.get("logo")),
            "name": self.current_user.company.get("abbreviation"),
            "image": self.static_url(self.current_user.company.get("conf_search_img")),
            "search_seq": search_seq
        })

        self.render("company/search.html", company=company)
