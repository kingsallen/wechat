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
        response = ObjectDict({'status': 1, 'message': 'failure'})
        if self.json_args and 'status' in self.json_args.keys():
            # Debug with front page.
            # To be confirmed: company_id, user_id
            self.json_args['company_id'] = 456
            self.json_args['user_id'] = 323

            if int(self.json_args.get('status')) == 0:
                response.message = 'ignore'
            else:
                resp = yield self.user_company_ps.set_visit_company(
                                    self.json_args)
                if resp:
                    response.status, response.message = 0, 'success'

        self._send_json(data=None, status_code=response.status,
                        message=response.message)
        return


class CompanyFollowHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        response = ObjectDict({'status': 1, 'message': 'failure'})
        if self.json_args and 'status' in self.json_args.keys():

            # Debug with front page.
            # To be confirmed: company_id, user_id
            self.json_args['company_id'] = 456
            self.json_args['user_id'] = 323

            resp = yield self.user_company_ps.set_company_follow(
                                self.json_args)
            if resp:
                response.status, response.message = 0, 'success'

        self._send_json(data=None, status_code=response.status,
                       message=response.message)
        return


class CompanyHandler(BaseHandler):

    @gen.coroutine
    def get(self, company_id):
        team_flag = True if re.match('^/m/company/team', self.request.uri) \
                    else False
        param = ObjectDict({'user_id': 222, 'company_id': company_id})
        response = yield self.user_company_ps.get_companay_data(param, team_flag)

        # Debug with front page.
        # To be confirmed: company_id, user_id
        wechat = ObjectDict({'signature': 'alex-testing'})
        current_user = ObjectDict({'wechat': wechat})

        # self.send_json(response, additional_dump=True)
        data = {'current_user':current_user}
        self.render_page('company/profile.html', data=response.data)
        # self.render_page('company/profile.html', current_user=current_user)
        return


class CompanySurveyHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        """处理用户填写公司 survey 的 post api 请求"""
        self.guarantee('selected', 'other')

        _company_id = self.current_user.company.id
        _sysuser_id = self.current.sysuser.id
        _selected = ujson.dumps(self.params.selected)
        _other = self.params.other

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
