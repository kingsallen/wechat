# -*- coding=utf-8 -*-

import json
from dao.user.user_company_follows import UserCompanyFollowsDao
from dao.user.user_company_visit_req import UserCompanyVisitReqDao
from tornado.util import ObjectDict
from tornado import gen
from handler.base import BaseHandler
from utils.common.decorator import handle_response



class TestCompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        obj = UserCompanyFollowsDao()
        user = yield obj.get_list_by_conds('id=1', ['company_id', 'user_id'])
        # user = yield self.user_company_ps.get_company_follows("id=1")
        # self.write(json.dumps(user))
        print user

        follow_cmpy_ids = yield self.user_company_ps.get_following_companys(
            self.json_args['user_id'])

        visit_cmpy_ids = yield self.user_company_ps.get_visit_req_companys(
            self.json_args['user_id'])

        print follow_cmpy_ids
        print visit_cmpy_ids
        return
        # raise gen.Return(json.dumps(user))
