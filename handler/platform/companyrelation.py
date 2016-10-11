# coding=utf-8
from tornado.util import ObjectDict
from tornado import gen
from handler.base import BaseHandler
from utils.common.decorator import handle_response



class CompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def post(self):
        pass


class CompanyFollowHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        result = ObjectDict({
            'status': 0,
            'message': 'to be decided',
        })
        company = ObjectDict({
            'name': 'to be decided',
            'description': 'to be decided',
        })
        following_companys = self.user_company_ps


    @gen.coroutine
    def post(self):
        pass
