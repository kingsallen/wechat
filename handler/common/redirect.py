# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response
from urllib.parse import unquote


class RedirectHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        next_url = self.params.next_url
        if next_url:
            self.redirect(next_url)












