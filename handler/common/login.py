# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response


class LoginHandler(BaseHandler):

    def get(self):
        self.render("system/login.html", {})

    @gen.coroutine
    def post(self):
        pass


