# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen

import conf.path as path
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

        search_seq = yield self.landing_ps.make_search_seq(self.current_user.company)

        self.logger.debug("[landing] search_seq: %s" % search_seq)

        # selected = ObjectDict({
        #     "city":             self.params.city,
        #     "salary":           self.params.salary,
        #     "occupation":       self.params.occupation,
        #     "team_name":        self.params.team_name,
        #     "candidate_source": self.params.candidate_source,
        #     "employment_type":  self.params.employment_type,
        #     "degree":           self.params.degree,
        #     "did":              int(self.params.did) if self.params.did else 0,
        #     "custom":           self.params.custom
        # })
        #
        # search_seq = yield self.landing_ps.get_landing_item(self.current_user.company,
        #                                                     self.current_user.wechat.company_id, selected)

        company = ObjectDict({
            "logo": self.static_url(self.current_user.company.logo),
            "name": self.current_user.company.get("abbreviation"),
            "image": self.static_url(self.current_user.company.conf_search_img),
            "search_seq": search_seq
        })

        yield self._make_share_info(self.current_user.company)

        self.render(template_name="company/search.html", company=company)

    @gen.coroutine
    def _make_share_info(self, company_info):
        """构建 share 内容"""

        cover = self.static_url(company_info.logo)
        title = "{}高级搜索".format(company_info.abbreviation)
        description = ""

        link = self.make_url(
            path.SEARCH_FILITER,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            escape=["pid"]
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })
