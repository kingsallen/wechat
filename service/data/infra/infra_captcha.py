# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.tool.http_tool import http_post
import conf.path as path


class InfraCaptchaDataService(DataService):

    @gen.coroutine
    def post_verification(self, params):
        ret = yield http_post(path.INFRA_CAPTCHA, params)
        raise gen.Return(ret)
