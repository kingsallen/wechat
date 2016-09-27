# coding=utf-8

# @Time    : 9/18/16 17:09
# @Author  : panda (panyuxin@moseeker.com)
# @File    : wechat.py
# @DES     : 与微信 API 之间的交互

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import *
from utils.tool.http_tool import http_get, http_post

class WechatDataService(DataService):

    @gen.coroutine
    def get_userinfo(self, code, wechat):
        pass
