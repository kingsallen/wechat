# coding=utf-8


import ujson
import urllib.parse

import tornado.gen as gen
import tornado.httpclient
from tornado.util import ObjectDict

import conf.common as constant
from setting import settings


class WeChatOauthError(Exception):
    pass


class WeChatOauth2Service(object):
    """ 微信 OAuth 2.0 实现

    refer to:
    http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
    """
    async_http = tornado.httpclient.AsyncHTTPClient()

    def __init__(self, handler, wechat, redirect_url, scope, state=0):
        self._wechat = wechat,
        self._redirect_url = redirect_url
        self._scope = scope,
        self._state = state
        self._handler = handler
        # cached access_token
        self._access_token = None

    # PUBLIC API
    def get_oauth_code_base(self):
        """静默授权获取 code"""
        self._get_oauth_code(is_base=1)

    def get_oauth_code_userinfo(self):
        """正常授权获取 code"""
        self._get_oauth_code(is_base=0)

    @gen.coroutine
    def get_openid_unionid_by_code(self, code):
        access_token_info = yield self._get_access_token_by_code(code)
        if 'errorcode' in access_token_info:
            raise WeChatOauthError(access_token_info.errmsg)
        else:
            openid = access_token_info.get('open_id')
            unionid = access_token_info.get('union_id')
            # 缓存 access_token
            self._access_token = access_token_info.get('access_token')
        raise gen.Return((openid, unionid))

    @gen.coroutine
    def get_userinfo_by_code(self, code):
        openid, _ = self.get_openid_unionid_by_code(code)
        userinfo = yield self._get_userinfo_by_openid(openid)
        if 'errorcode' in userinfo:
            raise WeChatOauthError(userinfo.errmsg)
        else:
            raise gen.Return(userinfo)

    # PROTECTED METHODS
    @staticmethod
    def _get_oauth_type(is_base):
        """获取 oauth_type"""
        if is_base:
            return "snsapi_base"
        else:
            return "snsapi_userinfo"

    def _get_oauth_code(self, is_base):
        if self._wechat.third_oauth:
            oauth_url = self._get_code_url_3rd_party(is_base)
        else:
            oauth_url = self._get_code_url(is_base)
        self._handler.logger.debug("oauth_url: {0}".format(oauth_url))
        self._handler.redirect(oauth_url)

    def _get_code_url(self, is_base=1):
        """非第三方获取 code 的 url"""

        return constant.WX_OAUTH_GET_CODE % (
            self._wechat.appid,
            urllib.parse.quote(self._redirect_url),
            self._scope,
            self._get_oauth_type(is_base),
            self._state)

    def _get_code_url_3rd_party(self, is_base=1):
        """第三方获取 code 的 url"""

        return constant.WX_THIRD_OAUTH_GET_CODE % (
            self._wechat.appid,
            urllib.parse.quote(self._redirect_url),
            self._scope,
            self._get_oauth_type(is_base),
            self._state,
            settings['component_app_id'])

    def _get_access_token_url(self, code):
        """生成获取 access_token 的 url"""
        if self._wechat.third_oauth:
            url = (constant.WX_THIRD_OAUTH_GET_ACCESS_TOKEN % (
                self._wechat.appid,
                code,
                settings["component_app_id"],
                settings["component_access_token"]))
        else:
            url = (constant.WX_OAUTH_GET_ACCESS_TOKEN % (
                self._wechat.appid,
                self._wechat.secret,
                code))
        return url

    @gen.coroutine
    def _get_access_token_by_code(self, code):
        """调用微信 Oauth get access token 接口
        :return: ObjectDict
        when success
        {
           "access_token":"ACCESS_TOKEN",
           "expires_in":7200,
           "refresh_token":"REFRESH_TOKEN",
           "openid":"OPENID",
           "scope":"SCOPE",
           "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        }

        when error
        {"errcode":40029,"errmsg":"invalid code"}
        """
        response = yield self.async_http.fetch(
            self._get_access_token_url(code))
        ret = ObjectDict(ujson.loads(response.body))
        raise gen.Return(ret)

    @gen.coroutine
    def _get_userinfo_by_openid(self, openid):
        """用 openid 拉取用户信息
        :return ObjectDict
        when success
        {
            "openid":" OPENID",
            " nickname": NICKNAME,
            "sex":"1",
            "province":"PROVINCE"
            "city":"CITY",
            "country":"COUNTRY",
            "headimgurl":    "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx",
            "privilege":[
            "PRIVILEGE1"
            "PRIVILEGE2"
            ],
            "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        }

        when error
        {"errcode":40003,"errmsg":" invalid openid"}
        """
        response = yield self.async_http.fetch(
            constant.WX_OAUTH_GET_USERINFO % (self._access_token, openid))

        ret = ObjectDict(ujson.loads(response.body))
        raise gen.Return(ret)
