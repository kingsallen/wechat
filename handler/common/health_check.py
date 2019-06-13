from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response


class HealthcheckHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        self.send_json_success(data={})
