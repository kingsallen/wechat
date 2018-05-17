# coding=utf-8

# @Author  : towry (wanglintao@moseeker.com)
# @File    : jslog.py

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response


class JSLogHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def post(self):
        """记录 js 日志"""

        self.logger.error("[JSLog] wechat_id: {0}, content: {1}".format(
            self.current_user.wechat.id, self.json_args))
        self.log_info = {
            "jslog": self.json_args
        }

        self.send_json_success()
