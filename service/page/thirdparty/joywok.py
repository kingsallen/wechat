# coding=utf-8

import re
import time
import traceback
import json
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import HTTPHeaders
import ujson

import conf.common as const
import conf.wechat as wx_const
import conf.message as message
from cache.user.user_hr_account import UserHrAccountCache
from service.page.base import PageService
from util.wechat.msgcrypt import WXBizMsgCrypt
from util.tool.url_tool import make_static_url
from util.tool.date_tool import curr_now
from util.tool.str_tool import mobile_validate, get_send_time_from_template_message_url
from util.common import ObjectDict
from util.tool.json_tool import json_dumps
from util.tool.http_tool import http_post
from util.wechat.core import get_wxuser, send_succession_message
from util.common.mq import user_follow_wechat_publisher, user_unfollow_wechat_publisher
from service.page.user.user import UserPageService

from setting import settings


class JoywokPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_joywok_info(self,  method, appid=None, code=None, headers=None):
        params = ObjectDict()
        if method == const.JMIS_USER_INFO:
            params = ObjectDict({
                "code": code,
                "method": method
            })
        elif method == const.JMIS_SIGNATURE:
            params = ObjectDict({
                "appid": appid,
                "method": method
            })
        ret = yield self.joywok_ds.get_joywok_info(params, headers)
        return ret


