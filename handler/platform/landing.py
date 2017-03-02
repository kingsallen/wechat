# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen

import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.url_tool import make_url
from util.common.cipher import encode_id


class LandingHandler(BaseHandler):
    """
    企业搜索页
    """

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

        self.logger.debug("[JD]构建转发信息")
        yield self._make_share_info(self.current_user.company)

        self.render(template_name="company/search.html", company=company)

    @gen.coroutine
    def _make_share_info(self, company_info):
        """构建 share 内容"""

        cover = self.static_url(company_info.logo)
        title = "{}高级搜索".format(company_info.abbreviation)
        description = ""

        link = make_url(
            path.SEARCH_FILITER,
            self.params,
            host=self.request.host,
            protocol=self.request.protocol,
            recom=self._make_recom(),
            escape=["pid"]
        )

        self.params.share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })

    def _make_recom(self):
        """用于微信分享和职位推荐时，传出的 recom 参数"""

        return encode_id(self.current_user.sysuser.id)

