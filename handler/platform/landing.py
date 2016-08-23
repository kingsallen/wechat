# coding=utf-8

# Copyright 2016 MoSeeker

from tornado.util import ObjectDict
from tornado import gen
from handler.base import BaseHandler
from utils.common.decorator import handle_response_error, url_valid

class LandingHandler(BaseHandler):

    """
    企业搜索页
    """

    @url_valid
    @handle_response_error
    @gen.coroutine
    def get(self):
        signature = str(self.get_argument("wechat_signature", ""))
        did = int(self.get_argument("did", 0))

        if signature:
            conds = {'signature': signature}
            wechat = yield self.wechat_ps.get_wechat(conds)
            company_id = wechat.get("company_id")
        else:
            self.write_error(404)
            return

        search_seq = yield self.landing_ps.get_landing_item(self.current_user.company, company_id)

        company = ObjectDict({
            "logo": self.current_user.company.get("logo"),
            "name": self.current_user.company.get("abbreviation"),
            "image": self.current_user.company.get("conf_search_img"),
            "search_seq" : search_seq
        })

        self.render("refer/neo_weixin/position/company_search.html", company=company, current_did=did)
