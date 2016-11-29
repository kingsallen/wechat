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
            "title": company_name + "的团队",
            "description": "",
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

        self.params.share = ObjectDict({
            "cover": self.static_url(self.current_user.company.logo),
            "title": team.name.upper() + "团队",
            "description": "",
            "link": self.fullurl
        })

        self.render_page(template_name='company/team.html', data=data)
        return
