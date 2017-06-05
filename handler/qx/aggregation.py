# coding=utf-8

# @Time    : 4/13/17 11:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

import ujson
from tornado import gen

import conf.path as path
import conf.qx as qx_const
from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.common import ObjectDict
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str


class AggregationHandler(BaseHandler):

    """
    聚合列表：企业+头图
    """

    @handle_response
    @gen.coroutine
    def get(self):

        search_dict = self._get_welcome_cookie()

        if self.params.keywords:
            # 带有keywords为主动搜索，不使用 cookie 缓存
            salary_top = self.params.salary_top
            salary_bottom = self.params.salary_bottom
            salary_negotiable = self.params.salary_negotiable
            keywords = self.params.keywords
            city = self.params.city
            industry = self.params.industry
        else:
            # 使用缓存的搜索条件
            salary_top = search_dict.get("salary_top", None)
            salary_bottom = search_dict.get("salary_bottom", None)
            salary_negotiable = search_dict.get("salary_negotiable", None)
            keywords = search_dict.get("keywords", None)
            city = search_dict.get("city", None)
            industry = search_dict.get("industry", None)

        did = self.params.did
        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10

        es_res, total = yield self.aggregation_ps.opt_es(salary_top,
                                                  salary_bottom,
                                                  salary_negotiable,
                                                  keywords,
                                                  city,
                                                  industry,
                                                  did,
                                                  int(page_no))

        positions = yield self.aggregation_ps.opt_agg_positions(es_res, int(page_no), int(page_size), self.current_user.sysuser.id, city)

        result = ObjectDict({
            "page_no": int(page_no),
            "page_size": int(page_size),
            "positions": positions,
            "total": total
        })

        if int(page_no) == 1:
            # 首页，需要头部信息
            # 处理头部 hr_ads
            is_show_ads = self._show_hr_ads()

            # 处理 banner
            banner = yield self.aggregation_ps.get_aggregation_banner()

            # 处理热招企业
            hot_company = yield self.aggregation_ps.opt_agg_company(es_res)

            # 自定义分享
            share = self._make_share_info(hot_company, keywords, self.current_user.company)

            # 构造搜索参数回显
            search_params = ObjectDict(
                salary_top=salary_top,
                salary_bottom=salary_bottom,
                salary_negotiable=salary_negotiable,
                keywords=keywords,
                city=city,
                industry=industry
            )

            result.update({
                "is_hr_ads": is_show_ads,
                "banner": banner,
                "hot_company": hot_company,
                "share": share,
                "search_params": search_params,
            })

            # 设置搜索词 cookie
            self._set_welcome_cookie()

        self.send_json_success(data=result)

    def _set_welcome_cookie(self):
        """用户在搜索页面点击“搜索”或者某个快速搜索条件的时候，系统会记录一个用户主动搜索的cookie。在
        1. 用户直接在移动浏览器或者微信访问www/m/mobile.moseeker.com的时候
        2. 用户的本次session是从访问《职位详情首页》/ 团队职位信息页 / 公司信息页 开始，并在访问期间点击以上页面的小圆点尝试返回职位列表的时候；

        如果浏览器发现没有该主动搜索的cookie，则到 初次进入页面；
        如果有主动搜索的cookie，则根据cookie的搜索条件，自动到该条件的搜索结果页面。
        """

        if self.params.salary_top or self.params.salary_bottom \
            or self.params.salary_negotiable or self.params.keywords \
            or self.params.city or self.params.industry:
            params = ObjectDict(
                salary_top=self.params.salary_top,
                salary_bottom=self.params.salary_bottom,
                salary_negotiable=self.params.salary_negotiable,
                keywords=self.params.keywords,
                city=self.params.city,
                industry=self.params.industry,
            )
            self.set_secure_cookie(
                qx_const.COOKIE_WELCOME_SEARCH,
                json_dumps(params))

    def _get_welcome_cookie(self):
        """获得 cookie 中的搜索记录，作为用户打开列表页的默认搜索条件"""

        search_keywords = to_str(self.get_secure_cookie(qx_const.COOKIE_WELCOME_SEARCH))
        search_dict = ObjectDict()
        if search_keywords:
            search_dict = ujson.loads(search_keywords)

        return search_dict

    def _show_hr_ads(self):
        """
        在用户不是通过《初次进入页面》进入该列表页面的情况下，
        在第一、二、三次session访问该列表页面的时候出现该层，
        每个session在本页面只出现一次。
        """
        session_ads = self.get_cookie(qx_const.COOKIE_HRADS_SESSIONS) or 0
        session_ads_total = self.get_cookie(qx_const.COOKIE_HRADS_TOTAL) or 0

        if session_ads:
            return False

        if not session_ads:
            self.set_cookie(
                qx_const.COOKIE_HRADS_SESSIONS,
                str(1),
                httponly=True)
            session_ads_total = int(session_ads_total) + 1
            self.logger.debug("session_ads_total 2:{}".format(session_ads_total))
            self.set_cookie(
                qx_const.COOKIE_HRADS_TOTAL,
                str(session_ads_total),
                httponly=True, expires_days=365)

        if int(session_ads_total) > 3:
            return False
        return True

    def _make_share_info(self, hot_company, keywords, company_info):
        """构建 share 内容"""

        link = self.make_url(
            path.GAMMA_POSITION,
            params=self.params,
            fr="recruit",
            recom=self.position_ps._make_recom(self.current_user.sysuser.id),
            escape=["page_no", "page_size"])

        if len(hot_company) == 1:
            logo = hot_company[0].get("logo")
        else:
            logo = company_info.logo

        cover = self.static_url(logo)
        keywords_title = "【{}】".format(keywords) if keywords else ""
        title = "%s职位推荐" % keywords_title
        description = "微信好友%s推荐%s的职位，点击查看详情。找的就是你！" % (self.current_user.qxuser.nickname or "", keywords_title)

        share = ObjectDict({
            "cover": cover,
            "title": title,
            "description": description,
            "link": link
        })

        return share
