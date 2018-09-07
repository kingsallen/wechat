# coding=utf-8
import hashlib
import json
import urllib.parse
import re

from tornado import gen

import conf.path as path
import conf.message as msg
import conf.common as const
from handler.base import BaseHandler
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated

from util.tool.str_tool import to_str, match_session_id
from util.tool.url_tool import make_url


class LoginTest(MetaBaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        data = ObjectDict(
            kind=1,  # // {0: success, 1: failure, 10: email}
            messages=['敬请期待'],  # ['hello world', 'abjsldjf']
            button_text=msg.BACK_CN,
            button_link=self.make_url(path.PROFILE_VIEW,
                                      self.params,
                                      host=self.host),
            jump_link=None  # // 如果有会自动，没有就不自动跳转
        )

        self.render_page(template_name="system/user-info.html",
                         data=data)
        return


class NormalTest(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        data = ObjectDict(
            kind=1,  # // {0: success, 1: failure, 10: email}
            messages=['感谢您的访问'],  # ['hello world', 'abjsldjf']
            button_text=msg.BACK_CN,
            button_link=self.make_url(path.PROFILE_VIEW,
                                      self.params,
                                      host=self.host),
            jump_link=None  # // 如果有会自动，没有就不自动跳转
        )

        self.render_page(template_name="system/user-info.html",
                         data=data)
        return









