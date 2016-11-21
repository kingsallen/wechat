# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""
from tornado import gen

from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import check_sub_company


class TeamIndexHandler(BaseHandler):
    @gen.coroutine
    @check_sub_company
    def get(self):
        template_name = 'company/team.html'
        current_company = self.params.pop('sub_company') if \
            self.params.sub_company else self.current_user.company

        data = yield self.team_ps.get_team_index(current_company, self.params)

        self.params.share = ObjectDict({
            "cover": self.static_url(current_company.logo),
            "title": current_company.name + "的团队",
            "description": "",
            "link": self.fullurl
        })

        self.render_page(template_name, data)
        return


class TeamDetailHandler(BaseHandler):
    @gen.coroutine
    @check_sub_company
    def get(self, team_id):
        print(team_id)
