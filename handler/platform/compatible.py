# coding=utf-8

# @Time    : 5/5/17 11:02
# @Author  : panda (panyuxin@moseeker.com)
# @File    : compatible.py
# @DES     :

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response
from conf import path


class CompatibleHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        if self.request.uri.startswith("/mobile/position") and self.params.m == "list":
            redirec_url = self.make_url(path=path.POSITION_LIST, params=self.params, host=self.host)
            self.logger.debug("[mobile position] redirect_url: {}".format(redirec_url))
            self.redirect(redirec_url)

