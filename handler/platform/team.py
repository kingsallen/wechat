# -*- coding=utf-8 -*-
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


class TeamIndexHandler(BaseHandler):

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

        company_name = current_company.abbreviation or current_company.name
        self.params.share = ObjectDict({
            "cover": self.static_url(current_company.logo),
            "title": company_name + "的核心团队点此查看",
            "description": u"这可能是你人生的下一站! 不先了解一下未来同事吗?",
            "link": self.fullurl
        })

        self.render_page(template_name, data)
        return


class TeamDetailHandler(BaseHandler):

    @check_sub_company
    @gen.coroutine
    def get(self, team_id):
        current_company = self.params.pop('sub_company') if \
            self.params.sub_company else self.current_user.company

        team = yield self.team_ps.get_team_by_id(team_id)
        if team.company_id != self.current_user.company.id:
            self.write_error(404)

        data = yield self.team_ps.get_team_detail(
            self.current_user, current_company, team, self.params)

        company_name = current_company.abbreviation or current_company.name

        # TODO: change share cover from company logo to the first picture in the team images.
        share_cover_url = self._get_share_image(data) or self.static_url(self.current_user.company.logo)
        self.params.share = ObjectDict({
            "cover": url_append_query(share_cover_url, "imageMogr2/thumbnail/!300x300r"),
            "title": team.name.upper() + "-" + company_name,
            "description": u'通常你在点击“加入我们”之类的按钮之前并不了解我们, 现在给你个机会!',
            "link": self.fullurl
        })

        self.render_page(template_name='company/team.html', data=data)
        return


    @staticmethod
    def _get_share_image(page_data):
        templates = page_data.templates
        template_media = templates[0] if len(templates) else None
        if not template_media:
            return None
        media_url = template_media.data.media_url if template_media.data else None
        return media_url
