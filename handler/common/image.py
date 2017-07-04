# coding=utf-8

import urllib.parse

from tornado import gen, httpclient

from handler.base import BaseHandler
from util.common.decorator import handle_response


class ImageFetchHandler(BaseHandler):
    """GET 请求获取 一个 image 并返回，主要用来清除 header 中的 referrer，
    目的是逃过防盗链检查
    
    """
    @handle_response
    @gen.coroutine
    def get(self):
        url = self.get_argument("url", None)
        if not url:
            self.write_error(http_code=404)
            return

        url = urllib.parse.unquote_plus(url)

        headers = {"Referer": ""}
        data = yield httpclient.AsyncHTTPClient().fetch(url, headers=headers)
        self.set_header("Content-Type", "image/jpeg")
        self.write(data.body)
