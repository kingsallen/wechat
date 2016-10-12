# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

import json
from tornado.util import ObjectDict
from tornado import gen
from handler.base import BaseHandler
from utils.tool.json_tool import json_dumps
from utils.common.decorator import handle_response


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

        self.write(json.dumps(response))
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

        self.write(json.dumps(response))
        return


class CompanyHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        if not self.json_args or 'company_id' not in self.json_args.keys() \
          or 'user_id' in self.json_args.keys():
            self.write(ObjectDict({'status': 1, 'message': 'failure'}))
        else:
            response = yield self.user_company_ps.get_companay_data(
                                self.json_args)

        return



