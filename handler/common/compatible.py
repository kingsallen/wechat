# coding=utf-8

# @Time    : 2/6/17 10:37
# @Author  : panda (panyuxin@moseeker.com)
# @File    : compatible.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

import conf.common as const
import conf.message as msg
import conf.path as path

from handler.base import BaseHandler
from util.common.decorator import handle_response
from util.tool.url_tool import make_url


class CompatibleHandler(BaseHandler):

    """兼容老微信企业号 url"""

    @handle_response
    @gen.coroutine
    def get(self):

        if self.is_platform:
            route = self.request.uri
            if route.startwith("/mobile/position") and self.params.m == "info":
                # JD 页
                replace_query = dict()
                self.redirect(make_url(path.POSITION_PATH.format(self.params.pid), self.params))
                return


            self.logger.debug("request: %s" % self.request)


    @handle_response
    @gen.coroutine
    def post(self):

        pass
