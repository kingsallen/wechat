# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.22

"""
from tornado import gen

from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import check_sub_company
from util.tool.url_tool import url_append_query
from util.common.decorator import handle_response
from tests.dev_data.user_company_config import COMPANY_CONFIG


class TeamIndexHandler(BaseHandler):

    @handle_response
    @check_sub_company
    @gen.coroutine
    def get(self):
        template_name = 'company/team.html'
        if self.params.sub_company:
            sub_company_flag = True
            current_company = self.params.pop('sub_company')
        else:
            sub_company_flag = False
            current_company = self.current_user.company

        data = yield self.team_ps.get_team_index(
            current_company, self.params, sub_company_flag)

        self.params.share = self._share(current_company)

        self.render_page(template_name, data)
        return

    def _share(self, company):
        config = COMPANY_CONFIG.get(company.id)
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": self.static_url(company.logo),
            "title": company_name + "的核心团队点此查看",
            "description": u"这可能是你人生的下一站! 不先了解一下未来同事吗?",
            "link": self.fullurl
        })
        if config.get('transfer', False) and config.transfer.get('tl', False):
            default.description = config.transfer.get('tl')

        return default


class TeamDetailHandler(BaseHandler):

    @handle_response
    @check_sub_company
    @gen.coroutine
    def get(self, team_id):
        current_company = self.params.pop('sub_company') if \
            self.params.sub_company else self.current_user.company

        team = yield self.team_ps.get_team_by_id(team_id)
        if team.company_id != self.current_user.company.id:
            self.write_error(404)
            return

        data = yield self.team_ps.get_team_detail(
            self.current_user, current_company, team, self.params)

        share_cover_url = data.templates[0].data[0].get('media_url') or \
            self.static_url(self.current_user.company.logo)
        self.params.share = self._share(current_company,
                                        team.name, share_cover_url)

        self.render_page(template_name='company/team.html', data=data)
        return

    def _share(self, company, team_name, share_cover_url):
        config = COMPANY_CONFIG.get(company.id)
        company_name = company.abbreviation or company.name
        default = ObjectDict({
            "cover": url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r"),
            "title": team_name.upper() + "-" + company_name,
            "description": u'通常你在点击“加入我们”之类的按钮之前并不了解我们, 现在给你个机会!',
            "link": self.fullurl
        })
        if config.get('transfer', False) and config.transfer.get('td', False):
            default.description = config.transfer.get('td')

        return default
