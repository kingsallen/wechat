# coding=utf-8

import re
import tornado.web


class WxoauthHandler(tornado.web.RequestHandler):
    def get(self):
        """接受仟寻公众号的授权，并回调到再次跳转的url
        """
        url = self.request.uri
        next_url = re.findall(r"\/wxoauth\?next_url=(.*)", url)
        self.redirect(next_url[0])
