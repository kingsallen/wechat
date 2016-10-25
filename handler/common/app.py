# coding=utf-8

from handler.base import BaseHandler

from tornado import gen


class IndexHandler(BaseHandler):
    """页面Index"""

    @gen.coroutine
    def get(self):
        try:
            self.render("system/app.html")

        except Exception as e:
            self.LOG.error(e)
