# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response


class UploadLoginHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):

        wx_login_args = dict(
            redirect_uri="http://www.moseeker.com",
            appid='',
            scope='',
            state='',
        )

        page_json = dict(
            wx_login_args=wx_login_args
        )

        self.render_page(
            template_name='employee/pc-qrcode-login.html',
            data=page_json)
