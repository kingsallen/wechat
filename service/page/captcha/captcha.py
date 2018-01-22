# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict


class CaptchaPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def post_verification(self, captcha, channel, account_id):
        """
        :param captcha: 回流的平台编号。1 前程无忧，2 猎聘，3 智联， 6 最佳东方， 7 一览英才
        :param channel: 验证码
        :param account_id: 第三方渠道账号ID
        :return:
        """

        req = ObjectDict({
            'info': captcha,
            'channel': channel,
            'accountId': account_id
        })
        res = yield self.infra_captcha_ds.post_verification(req)
        status, message = res.status, res.message
        return status, message
