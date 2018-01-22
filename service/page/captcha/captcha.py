# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict


class CaptchaPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def post_verification(self, captcha, channel, account_id):

        req = ObjectDict({
            'info': captcha,
            'channel': channel,
            'accountId': account_id
        })
        res = yield self.infra_captcha_ds.post_verification(req)
        status, message = res.status, res.message
        return status, message
