# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
import conf.common as const
from util.common import ObjectDict


class CaptchaHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        self.render(
            template_name=''
        )

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('captcha')
        except AttributeError:
            return
        captcha = self.params.captcha
        status, message = yield self.captcha_ps.get_verification(captcha)
        data = ObjectDict({'message': message})
        if status == 0:
            self.send_json_success(data=data)
        else:
            self.send_json_error(data=data)


