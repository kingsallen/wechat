# coding=utf-8

import json
import os
import re
import time
import traceback
from hashlib import sha1
from urllib.parse import unquote

from tornado import gen, locale

import conf.common as const
import conf.path as path
import conf.wechat as wx_const
from cache.user.passport_session import PassportCache
from handler.metabase import MetaBaseHandler
from oauth.wechat import WeChatOauth2Service, WeChatOauthError, JsApi
from setting import settings
from util.common import ObjectDict
from util.common.cipher import decode_id
from util.common.decorator import check_signature
from util.tool.date_tool import curr_now
from util.tool.str_tool import to_str, from_hex, match_session_id, \
    languge_code_from_ua
from util.tool.url_tool import url_subtract_query, make_url


class WorkwxHandler(MetaBaseHandler):
    """Handler 基类, 仅供微信端网页调用

    不要使用（创建）get_current_user()
    get_current_user() 不能为异步方法，而 parpare() 可以
    self.current_user 将在 prepare() 中以 self.current_user = XXX 的形式创建
    Refer to:
    http://www.tornadoweb.org/en/stable/web.html#other
    """

    def __init__(self, application, request, **kwargs):
        super(WorkwxHandler, self).__init__(application, request, **kwargs)

        # 构建 session 过程中会缓存一份当前公众号信息
        self._wechat = None

    # PUBLIC API
    @check_signature
    @gen.coroutine
    def prepare(self):
        """用于生成 current_user"""
        session = ObjectDict()
        self._wechat = yield self._get_current_wechat()
        session.wechat = self._wechat
        self.current_user = session  #前端用

        # 内存优化
        self._wechat = None

        self.logger.debug("current_user:{}".format(self.current_user))
        self.logger.debug("+++++++++++++++++PREPARE OVER+++++++++++++++++++++")

    @gen.coroutine
    def _get_current_wechat(self, qx=False):
        if qx:
            signature = self.settings['qx_signature']
        else:
            signature = self.params['wechat_signature']
        wechat = yield self.wechat_ps.get_wechat(conds={
            "signature": signature
        })
        if not wechat:
            self.write_error(http_code=404)
            return

        raise gen.Return(wechat)
