# coding=utf-8

import json

import tornado.httpclient
from tornado import gen
from setting import settings
from conf import common as constant
from tornado.util import ObjectDict


class WeixinAsyncApi():
    def __init__(self, access_token=None, appid=None, appsecret=None, component_access_token=None):
        self.access_token = access_token
        self.appid = appid
        self.appsecret = appsecret
        self.component_access_token = component_access_token
        self.httpclient = tornado.httpclient.AsyncHTTPClient()

    @gen.coroutine
    def get_openid_by_code(self, code, wechat, **kwargs):

        if wechat.third_oauth == 1:
            component_appid = settings["component_app_id"]
            url = (constant.WX_THIRD_OAUTH_GET_ACCESS_TOKEN % (self.appid, code, component_appid, self.component_access_token))
        else:
            url = (constant.WX_OAUTH_GET_ACCESS_TOKEN % (self.appid, self.appsecret, code))

        res = yield self.httpclient.fetch(url, **kwargs)

        raise gen.Return(res)

    @gen.coroutine
    def get_userinfo_by_code(self, code, wechat, **kwargs):

        if wechat.third_oauth == 1:
            component_appid = settings["component_app_id"]
            url = (constant.WX_THIRD_OAUTH_GET_ACCESS_TOKEN % (self.appid, code, component_appid, self.component_access_token))
        else:
            url = (constant.WX_OAUTH_GET_ACCESS_TOKEN % (self.appid, self.appsecret, code))

        res = yield self.httpclient.fetch(url, **kwargs)

        userinfo = yield self.get_wxuser_info(ObjectDict(json.loads(res.body), default=""))

        raise gen.Return(userinfo)

    @gen.coroutine
    def get_wxuser_info(self, response):
        if not response:
            raise gen.Return(None)
        url = (constant.WX_OAUTH_GET_USERINFO % (response.access_token, response.openid))
        userinfo = yield self.httpclient.fetch(url)
        raise gen.Return(userinfo)

    @staticmethod
    def callback_get_openid_by_code(response):
        res = ObjectDict(json.loads(response.body))
        return res if res.openid and res.access_token else None
