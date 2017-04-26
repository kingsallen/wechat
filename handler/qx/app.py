# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response


class IndexHandler(BaseHandler):
    """页面Index, Gamma单页应用使用"""

    @handle_response
    @gen.coroutine
    def get(self):
        self.logger.debug("IndexHandler qx")
        self.render(template_name="qx/qx.html")
