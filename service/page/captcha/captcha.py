# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict


class CaptchaPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_verification(self, captcha):

        req = ObjectDict({
            'captcha': captcha
        })
        res = yield self.infra_captcha_ds.get_verification(req)
        status, message = res.status, res.message
        return status, message
