# coding=utf-8

from tornado import gen
from handler.base import MetaBaseHandler
from util.common.decorator import handle_response,common_handler


@common_handler
class HealthcheckHandler(MetaBaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        self.send_json_success(data={})
