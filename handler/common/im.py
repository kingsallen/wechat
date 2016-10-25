# coding=utf-8

from handler.base import BaseHandler

from tornado import gen


class UnreadCountHandler(BaseHandler):

    @gen.coroutine
    def get(self):
       pass

