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


class CompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        self.guarantee('status')
        result = yield self.user_company_ps.set_visit_company(self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyFollowHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        self.guarantee('status')
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
        response = yield self.user_company_ps.get_companay_data(param, team_flag)

        self.render_page('company/profile.html', data=response.data)
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
