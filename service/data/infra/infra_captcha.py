# coding=utf-8

from tornado import gen
from service.data.base import DataService
from util.tool.http_tool import http_post, http_get
import conf.path as path


class InfraCaptchaDataService(DataService):

    @gen.coroutine
    def post_verification(self, params):
        ret = yield http_post(path.INFRA_CAPTCHA, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_verification_params(self, params):
        ret = yield http_get(path.INFRA_VERIFY_PARAMS, params)
        raise gen.Return(ret)
