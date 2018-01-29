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
    生成验证码页面
    """
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        param_id = self.params.paramId
        message, body, status = yield self.captcha_ps.get_verification_params(param_id)
        if status == 61010:
            data = ObjectDict(
                kind=0,  # // {0: success, 1: failure, 10: email}
                massages=msg.CAPTCHA_SUCCESS,  # ['hello world', 'abjsldjf']
                jump_link=None  # // 如果有会自动，没有就不自动跳转
            )
            self.render_page(template_name="system/user-info.html",
                             data=data)
            return

        messages = []
        if not body:
            messages.append(message)
            messages.append("请登录hr.moseeker.com重新同步职位")
            data = ObjectDict(
                kind=1,  # // {0: success, 1: failure, 10: email}
                massages=messages,  # ['hello world', 'abjsldjf']
                jump_link=None  # // 如果有会自动，没有就不自动跳转
            )

            self.render_page(template_name="system/user-info.html",
                             data=data)
        else:
            self.render_page(
                template_name='adjunct/validate-captcha.html',
                data=body
            )


class CaptchaCheckHandler(BaseHandler):
    """
    校验验证码
    """
    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('captcha', 'channel')
        except AttributeError:
            return
        channel = self.params.channel
        account_id = self.json_args.accountId
        captcha = self.params.captcha
        position_id = self.json_args.positionId
        param_id = self.json_args.paramId
        status, message = yield self.captcha_ps.post_verification(captcha, channel, account_id, position_id, param_id)
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
            massages=msg.CAPTCHA_SUCCESS,  # ['hello world', 'abjsldjf']
            jump_link=None  # // 如果有会自动，没有就不自动跳转
        )

        self.render_page(template_name="system/user-info.html",
                         data=data)
        return

