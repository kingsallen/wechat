# coding=utf-8
from tornado.util import ObjectDict
from tornado import gen
from handler.base import BaseHandler
from utils.common.decorator import handle_response



class CompanyVisitReqHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        pass

    @gen.coroutine
    def post(self):
        pass


class CompanyFollowHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        pass

    @gen.coroutine
    def post(self):
        pass
