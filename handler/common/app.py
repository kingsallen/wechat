# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response


class IndexHandler(BaseHandler):
    """页面Index"""

    @handle_response
    @gen.coroutine
    def get(self):

        self.render(template_name="system/app.html")
