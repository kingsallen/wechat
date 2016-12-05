# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""
import ujson

from tornado import gen
from util.common import ObjectDict
from util.common.decorator import check_sub_company
from handler.base import BaseHandler


class CompanyVisitReqHandler(BaseHandler):

    @check_sub_company
    @gen.coroutine
    def post(self):
        self.guarantee('status')
        result = yield self.user_company_ps.set_visit_company(
            current_user=self.current_user, param=self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyFollowHandler(BaseHandler):

    @check_sub_company
    @gen.coroutine
    def post(self):
        self.guarantee('status')
        result = yield self.user_company_ps.set_company_follow(
            current_user=self.current_user, param=self.params)

        if not result:
            self.send_json_error()
            return
        self.send_json_success()


class CompanyHandler(BaseHandler):

    @check_sub_company
    @gen.coroutine
    def get(self):
        company = self.params.pop('sub_company') if self.params.sub_company \
            else self.current_user.company

        data = yield self.user_company_ps.get_company_data(
            self.params, company, self.current_user)

        company_name = company.abbreviation or company.name
        self.params.share = ObjectDict({
            'cover':       self.static_url(self.current_user.company.logo),
            'title':       company_name + ', 我发现了一个好公司！',
            'description': '',
            'link':        self.fullurl
        })

        self.render_page(template_name='company/profile.html', data=data)
        return


class CompanySurveyHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        """处理用户填写公司 survey 的 post api 请求"""
        self.guarantee('selected', 'other')

        _company_id = self.current_user.company.id
        _sysuser_id = self.current_user.sysuser.id
        _selected = ujson.dumps(self.params.selected, ensure_ascii=False)
        _other = self.params.other or ''

        inserted_id = yield self.company_ps.save_survey({
            'company_id': _company_id,
            'sysuser_id': _sysuser_id,
            'selected': _selected,
            'other': _other
        })

        if inserted_id and int(inserted_id):
            self.send_json_success()
        else:
            self.send_json_error()
