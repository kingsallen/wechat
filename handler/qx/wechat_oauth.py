# coding=utf-8

import re
import urllib.parse

import tornado.web


class WxOauthHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        # 日志需要，由 route 定义
        self.event = kwargs.get("event")

    def get(self):
        """接受仟寻公众号的授权，并回调到再次跳转的url
        """
        url = self.request.uri
        next_url = urllib.parse.unquote(
            re.findall(r"/wxoauth2\?next_url=(.*)", url)[0])
        self.redirect(next_url)
        return
