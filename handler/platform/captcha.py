# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
import conf.common as const
from util.common import ObjectDict
from util.tool.url_tool import make_url
import conf.path as path
import conf.message as msg


class CaptchaHandler(BaseHandler):
    """
    处理验证码
    """
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        param_id = self.params.paramId
        data = yield self.captcha_ps.get_verification_params(param_id)
        if not data:
            self.write_error(500, message="请求失败，请重试")
        else:
            self.render(
                template_name='template/adjunct/validate-captcha.html',
                data=data
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
        next_url = make_url(path.CAPTCHA_CHECKED, host=self.host)
        if status == 0:
            data = ObjectDict({
                'status': True,
                'message': message,
                'next_url': next_url
            })
            self.send_json_success(data=data)
        else:
            data = ObjectDict({
                'status': False,
                'message': message
            })
            self.send_json_error(data=data)


class CaptchaChecked(BaseHandler):
    """
    验证成功后返回的页面
    """
    def get(self):

        data = ObjectDict(
            kind=0,  # // {0: success, 1: failure, 10: email}
            massage=msg.CAPTCHA_SUCCESS,  # ['hello world', 'abjsldjf']
            jump_link=None  # // 如果有会自动，没有就不自动跳转
        )

        self.render_page(template_name="system/user-info.html",
                         data=data)
        return

