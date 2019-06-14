# coding=utf-8

from tornado import gen
from handler.base import BaseHandler, MetaBaseHandler
from util.common.decorator import handle_response
from urllib.parse import unquote


class RedirectHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        next_url = self.params.next_url
        if next_url:
            self.redirect(next_url)


class H5DefaultHandler(MetaBaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, h5_id):
        self.render_page(template_name="adjunct/page-expired.html", data={}, message='该页面已过保质期', meta_title='页面已过期')








