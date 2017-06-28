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

        self.debug("[landing] search_seq: %s" % search_seq)

        company = ObjectDict({
            "logo": self.static_url(self.current_user.company.logo),
            "name": self.current_user.company.get("abbreviation"),
            "image": self.static_url(self.current_user.company.conf_search_img),
            "search_seq": search_seq
        })

        yield self._make_share_info(self.current_user.company)

        self.render_page(template_name="company/dynamic_search.html", data=company)

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
