# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common
import conf.common as const


class UploadHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def post(self):
        













