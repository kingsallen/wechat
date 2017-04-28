# coding=utf-8

# @Time    : 4/13/17 11:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

from tornado import gen

import conf.common as const
import conf.path as path
import conf.qx as qx_const
from handler.base import BaseHandler
from util.common.decorator import handle_response, gamma_welcome
from util.common import ObjectDict
from util.tool.url_tool import make_static_url


class AggregationHandler(BaseHandler):

    """
    聚合列表：企业+头图
    """

    @handle_response
    # @gamma_welcome
    @gen.coroutine
    def get(self):

        salary_top = self.params.salary_top
        salary_bottom = self.params.salary_bottom
        salary_negotiable = self.params.salary_negotiable
        keywords = self.params.keywords
        city = self.params.city
        industry = self.params.industry
        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10

        es_res = yield self.aggregation_ps.opt_es(salary_top,
                                                  salary_bottom,
                                                  salary_negotiable,
                                                  keywords,
                                                  city,
                                                  industry,
                                                  int(page_no),
                                                  int(page_size))

        positions = yield self.aggregation_ps.opt_agg_positions(es_res, page_size, self.current_user.sysuser.id)

        result = ObjectDict({
            "page_no": page_no,
            "page_size": page_size,
            "positions": positions,
        })

        if int(page_no) == 1:
            # 首页，需要头部信息
            # 处理头部 hr_ads
            is_show_ads = self._show_hr_ads()

            # 处理 banner
            banner = yield self.aggregation_ps.get_aggregation_banner()

            # 处理热招企业
            hot_company = self.aggregation_ps.opt_agg_company(es_res)

            # 自定义分享
            share = self._make_share_info(hot_company)

            result.update({
                "is_hr_ads": is_show_ads,
                "banner": banner,
                "hot_company": hot_company,
                "share": share,
            })

            # 来自初次进入页面，则设置搜索词 cookie
            if self.params.fr_wel:
                self._set_welcome_cookie()

        self.send_json_success(data=result)

    def _set_welcome_cookie(self):
        """用户在搜索页面点击“搜索”或者某个快速搜索条件的时候，系统会记录一个用户主动搜索的cookie。在
        1. 用户直接在移动浏览器或者微信访问www/m/mobile.moseeker.com的时候
        2. 用户的本次session是从访问《职位详情首页》/ 团队职位信息页 / 公司信息页 开始，并在访问期间点击以上页面的小圆点尝试返回职位列表的时候；

        如果浏览器发现没有该主动搜索的cookie，则到 初次进入页面；
        如果有主动搜索的cookie，则根据cookie的搜索条件，自动到该条件的搜索结果页面。
        """
        if self.params.keywords:
            self.set_secure_cookie(
                qx_const.COOKIE_WELCOME_SEARCH,
                self.params.keywords,
                httponly=True)

    def _show_hr_ads(self):
        """
        在用户不是通过《初次进入页面》进入该列表页面的情况下，
        在第一、二、三次session访问该列表页面的时候出现该层，
        每个session在本页面只出现一次。
        """
        session_ads = self.get_cookie(qx_const.COOKIE_HRADS_SESSIONS) or 0
        session_ads_total = self.get_cookie(qx_const.COOKIE_HRADS_TOTAL) or 0

        if not session_ads:
            self.set_cookie(
                qx_const.COOKIE_HRADS_SESSIONS,
                str(1),
                httponly=True)
            session_ads_total = int(session_ads_total) + 1
            self.set_cookie(
                qx_const.COOKIE_HRADS_TOTAL,
                str(session_ads_total),
                httponly=True, expires_days=365)
        if int(session_ads_total) > 3:
            return False
        return True

    def _make_share_info(self, hot_company):
        """构建 share 内容"""

        link = self.make_url(
            path.GAMMA_POSITION,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            escape=["page_no", "page_size"])

        if len(hot_company) == 1:
            logo = hot_company[0].get("logo")
        else:
            logo = make_static_url(const.COMPANY_HEADIMG)

        cover = self.static_url(logo)
        keywords = "【%s】".format(self.params.keywords) if self.params.keywords else ""
        title = "%s职位推荐" % keywords
        description = "微信好友%s推荐%s的职位，点击查看详情。找的就是你！" % (self.current_user.qxuser.nickname or "", keywords)

        share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })

        return share
