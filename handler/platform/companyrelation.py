# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from tornado import gen
from tornado.util import ObjectDict
from handler.base import BaseHandler


class CompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        response = ObjectDict({'status': 1, 'message': 'failure'})
        if self.json_args and 'company_id' in self.json_args.keys() \
            and 'user_id' in self.json_args.keys() \
            and 'status' in self.json_args.keys():
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
        if self.json_args and 'company_id' in self.json_args.keys() \
            and 'user_id' in self.json_args.keys() \
            and 'status' in self.json_args.keys():
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

        self.send_json(response, additional_dump=True)
        return



