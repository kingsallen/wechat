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

    @gen.coroutine
    def get_verification_params(self, param_id):
        """
        获取生成验证页面的相关参数
        :param param_id:
        :return:
        """
        req = ObjectDict({'paramId': param_id})
        res = yield self.infra_captcha_ds.get_verification_params(req)
        message, data = res.message, res.data
        ret = ObjectDict()
        if data:
            ret['channel'] = data.channel
            ret['accountId'] = data.accounrId
            ret['mobile'] = data.mobile
        return message, ret


