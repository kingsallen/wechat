# coding=utf-8

from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response


class InterviewStatisticsHandler(BaseHandler):
    """借助stats做数据统计，统计button的点击次数"""
    @handle_response
    @gen.coroutine
    def get(self):
        self.send_json_success()
