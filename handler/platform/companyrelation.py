# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""
import re
from tornado import gen
from util.common import ObjectDict
from handler.base import BaseHandler
import ujson
import conf.common as const


class CompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        self.guarantee('status')
        self.params.company_id = self.current_user.company.id
        self.params.user_id = self.current_user.sysuser.id
        result = yield self.user_company_ps.set_visit_company(self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyFollowHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        self.guarantee('status')
        self.params.company_id = self.current_user.company.id
        self.params.user_id = self.current_user.sysuser.id
        result = yield self.user_company_ps.set_company_follow(self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        team_flag = True if re.match('^/m/company/team', self.request.uri) \
                    else False
        param = ObjectDict({
            'user_id': self.current_user.sysuser.id,
            'company_id': self.current_user.company.id
        })
        response = yield self.user_company_ps.get_companay_data(
            handler_params=self.params,
            param=param,
            team_flag=team_flag)

        template_name = 'company/team.html' if team_flag \
                         else 'company/profile.html'

        company_name = self.current_user.company.abbreviation or self.current_user.company.name
        if team_flag:
            self.params.share = ObjectDict({
                "cover":       self.static_url(self.current_user.company.logo),
                "title":       company_name + "的团队",
                "description": "",
                "link":        self.fullurl
            })
        else:
            self.params.share = ObjectDict({
                "cover":       self.static_url(self.current_user.company.logo),
                "title":       company_name + ", 我发现了一个好公司！",
                "description": "",
                "link":        self.fullurl
            })

        self.render_page(template_name, data=response.data)
        return


class CompanyTeamHandler(BaseHandler):

    @gen.coroutine
    def get(self, team_name):
        self.params.company_id = self.current_user.company.id
        self.params.user_id = self.current_user.sysuser.id
        result = yield self.team_ps.get_more_team_info(team_name, params=self.params)
        # icon 为空，出来统一赋值
        result.header.icon = self.static_url(self.current_user.company.logo)



        self.params.share = ObjectDict({
            "cover":       self.static_url(self.current_user.company.logo),
            "title":       team_name.upper() + "团队",
            "description": "",
            "link":        self.fullurl
        })

        self.render_page(template_name='company/team.html', data=result)
        return


class CompanySurveyHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        """处理用户填写公司 survey 的 post api 请求"""
        self.guarantee('selected', 'other')

        _company_id = self.current_user.company.id
        _sysuser_id = self.current_user.sysuser.id
        _selected = ujson.dumps(self.params.selected, ensure_ascii=False)
        _other = self.params.other or ""

        inserted_id = yield self.company_ps.save_survey({
            "company_id": _company_id,
            "sysuser_id": _sysuser_id,
            "selected": _selected,
            "other": _other
        })

        if inserted_id and int(inserted_id):
            self.send_json_success()
        else:
            self.send_json_error()
