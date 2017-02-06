# coding=utf-8

# @Time    : 2/6/17 10:37
# @Author  : panda (panyuxin@moseeker.com)
# @File    : compatible.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

import conf.common as const
import conf.message as msg

from handler.base import BaseHandler
from util.common.decorator import handle_response


class CompatibleHandler(BaseHandler):

    """兼容老微信企业号 url"""

    @handle_response
    @gen.coroutine
    def get(self):

        if self.is_platform:
            self.logger.debug("request: %s" % self.request)







    @handle_response
    @gen.coroutine
    def post(self):

        pass
