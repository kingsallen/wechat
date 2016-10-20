# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from tornado import gen
from util.common import ObjectDict
from handler.base import BaseHandler


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

        self.send_json(response)
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

        self.send_json(response)
        return


class CompanyHandler(BaseHandler):

    @gen.coroutine
    def get(self, company_id):
        param = ObjectDict({'user_id': 222, 'company_id': company_id})
        response = yield self.user_company_ps.get_companay_data(param)

        # Debug with front page.
        # To be confirmed: company_id, user_id
        wechat = ObjectDict({'signature': 'alex-testing'})
        current_user = ObjectDict({'wechat': wechat})

        self.send_json(response, additional_dump=True)
        # self.render('company/profile.html', current_user=current_user)
        return
