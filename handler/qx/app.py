# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, gamma_welcome


class IndexHandler(BaseHandler):
    """页面Index, Gamma单页应用使用"""

    @handle_response
    @gamma_welcome
    @gen.coroutine
    def get(self):
        self.logger.debug("qx IndexHandler")

        self.render(template_name="qx/qx.html")


class NotFoundHandler(BaseHandler):

    @handle_response
    def get(self):
        self.send_json_error(message="not found", http_code=404)

    @handle_response
    def post(self):
        self.send_json_error(message="not found", http_code=404)
