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
    def get(self):
        template_name = 'company/team.html'
        sub_company_id = self.params.get('did', None)

        if sub_company_id is not None:
            sub_company = self.team_ps.get_sub_company(sub_company_id)
            if sub_company.parent_id != self.current_user.company.id:
                self.write_error(404)
                return
            else:
                # 子公司
                share_company = 'sub_company'
                pass
        else:
            # 母公司显示全部团队列表
            data = yield self.team_ps.get_team_index(
                company=self.current_user.company,
                hander_params=self.params
            )
            share_company = self.current_user

        self.params.share = ObjectDict({
            "cover": self.static_url(share_company.logo),
            "title": share_company.name + "的团队",
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
