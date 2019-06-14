# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response,common_handler


class HealthcheckHandler(BaseHandler):
    @common_handler
    @handle_response
    @gen.coroutine
    def get(self):
        self.send_json_success(data={})
