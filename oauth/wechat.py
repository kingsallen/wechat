# coding=utf-8

from urllib.parse import quote
import tornado.gen as gen

import conf.wechat as wx_const

from util.common.sign import Sign
from util.tool.http_tool import http_get

from globals import logger
from setting import settings


class WeChatOauthError(Exception):
    pass


class WeChatOauth2Service(object):
    """ 微信 OAuth 2.0 实现

    refer to:
    http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
    """

    def __init__(self, wechat, redirect_url, component_access_token):
        self.redirect_url = redirect_url
        self.wechat = wechat
        self.state = 0

        # 第三方的 component_access_token
        self._component_access_token = component_access_token

        # 缓存 access_token
        self._access_token = None

    # PUBLIC API
    def get_oauth_code_base_url(self):
        """静默授权获取 code"""
        return self._get_oauth_code_url(is_base=1)

    def get_oauth_code_userinfo_url(self):
        """正常授权获取 code"""
        return self._get_oauth_code_url(is_base=0)

    @gen.coroutine
    def get_openid_unionid_by_code(self, code):
        """根据 code 尝试获取 openid 和 unionoid
        :param code: code
        :return:
        """
        access_token_info = yield self._get_access_token_by_code(code)
        if access_token_info.errcode:
            raise WeChatOauthError("get_openid_unionid_by_code: {}".format(access_token_info.errmsg))
        else:
            openid = access_token_info.get('openid')
            unionid = access_token_info.get('unionid')
            # 缓存 access_token
            self._access_token = access_token_info.get('access_token')
        raise gen.Return((openid, unionid))

    @gen.coroutine
    def get_userinfo_by_code(self, code):
        """根据 code 尝试获取 userinfo
        :param code:
        :return:
        """
        openid, _ = yield self.get_openid_unionid_by_code(code)
        userinfo = yield self._get_userinfo_by_openid(openid)
        if userinfo.errcode:
            raise WeChatOauthError("get_userinfo_by_code: {}".format(userinfo.errmsg))
        else:
            raise gen.Return(userinfo)

    # PROTECTED METHODS
    @staticmethod
    def _get_oauth_type(is_base):
        """根据 is_base 生成 scope 字符串"""
        if is_base:
            return wx_const.SCOPE_BASE
        else:
            return wx_const.SCOPE_USERINFO

    def _get_oauth_code_url(self, is_base):
        """生成获取 code 的 url

        根据微信判断是否使用第三方
        """
        if self.wechat.third_oauth:
            oauth_url = self._get_code_url_3rd_party(is_base)
        else:
            oauth_url = self._get_code_url(is_base)
        logger.debug("get_code_url: {0}".format(oauth_url))
        return oauth_url

    def _get_code_url(self, is_base=1):
        """非第三方获取 code 的 url"""
        # self.__adjust_url(is_base)

        return wx_const.WX_OAUTH_GET_CODE % (
            self.wechat.appid,
            quote(self.redirect_url),
            self._get_oauth_type(is_base),
            self.state)

    def _get_code_url_3rd_party(self, is_base=1):
        """第三方获取 code 的 url"""
        # self.__adjust_url(is_base)

        return wx_const.WX_THIRD_OAUTH_GET_CODE % (
            self.wechat.appid,
            quote(self.redirect_url),
            self._get_oauth_type(is_base),
            self.state,
            settings['component_app_id'])

    def _get_access_token_url(self, code):
        """生成获取 access_token 的 url"""
        if self.wechat.third_oauth:
            url = (wx_const.WX_THIRD_OAUTH_GET_ACCESS_TOKEN % (
                    self.wechat.appid,
                    code,
                    settings["component_app_id"],
                    self._component_access_token))
        else:
            url = (wx_const.WX_OAUTH_GET_ACCESS_TOKEN % (
                    self.wechat.appid,
                    self.wechat.secret,
                    code))
        logger.debug("get_access_token_url: {0}".format(url))
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
        ret = yield http_get(self._get_access_token_url(code), infra=False)
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
        ret = yield http_get(wx_const.WX_OAUTH_GET_USERINFO % (self._access_token, openid), infra=False)
        raise gen.Return(ret)


class JsApi(object):
    """初始化 JsApi"""
    def __init__(self, jsapi_ticket, url):
        self.sign = Sign(jsapi_ticket=jsapi_ticket)
        self.__dict__.update(self.sign.sign(url=url))

