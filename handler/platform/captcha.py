# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
import conf.common as const
from util.common import ObjectDict


class CaptchaHandler(BaseHandler):
    """
    处理验证码
    """
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        channel = self.params.channel
        accountId = self.params.accountId
        self.render(
            template_name='',
            channel=channel,
            accountId=accountId
        )

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('captcha', 'channel')
        except AttributeError:
            return
        channel = self.params.channel
        account_id = self.params.accountId
        captcha = self.json_args.captcha
        status, message = yield self.captcha_ps.post_verification(captcha, channel, account_id)

        if status == 0:
            data = ObjectDict({
                'status': True,
                'message': message
            })
            self.send_json_success(data=data)
        else:
            data = ObjectDict({
                'status': False,
                'message': message
            })
            self.send_json_error(data=data)


