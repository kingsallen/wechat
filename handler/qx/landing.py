# coding=utf-8

from tornado import gen
from handler.base import BaseHandler


class LandingHandler(BaseHandler):
    """聚合号的企业主页
    """

    @gen.coroutine
    def get(self):
        pass
