# coding=utf-8


import re
import ujson
from urllib.parse import urlparse, quote

import tornado.gen as gen
import tornado.httpclient

import conf.common as const
import conf.wechat as wx_const
import conf.path as path

from util.common import ObjectDict
from util.common.sign import Sign

from app import logger
from setting import settings


class WeChatOauthError(Exception):
    pass


class WeChatOauth2Service(object):
    """ 微信 OAuth 2.0 实现

    refer to:
    http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
    """
    async_http = tornado.httpclient.AsyncHTTPClient()

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

    @property
    def handling_qx(self):
        return self.wechat.id == settings['qx_wechat_id']

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
        self.__adjust_url(is_base)

        return wx_const.WX_OAUTH_GET_CODE % (
            self.wechat.appid,
            quote(self.redirect_url),
            self._get_oauth_type(is_base),
            self.state)

    def _get_code_url_3rd_party(self, is_base=1):
        """第三方获取 code 的 url"""
        self.__adjust_url(is_base)

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
            wx_const.WX_OAUTH_GET_USERINFO % (self._access_token, openid))

        ret = ObjectDict(ujson.loads(response.body))
        raise gen.Return(ret)

    def __adjust_url(self, is_base):
        """必要时调整 redirect_uri 的二级域名

        '必要时'指： 1.静默授权
                    2. wechat 实例变量是聚合号
                    3. redirect_url 是 platform 开头

        将 redirect_url 改为 qx 域名，并使用跳转 url，
        将现有 redirect_url 填充 next_url 参数
        """

        if not is_base and self.handling_qx and self.__is_platform_url(
                self.redirect_url):
            next_url = quote(self.redirect_url)
            up = urlparse(self.redirect_url)
            netloc = up.netloc.replace(const.ENV_PLATFORM, const.ENV_QX, 1)
            self.redirect_url = "{}?next_url={}".format(
                up.scheme + "://" + netloc + path.WX_OAUTH_QX_PATH,
                next_url)

    @staticmethod
    def __is_platform_url(string):
        """判断是否是 platform 的 url"""
        regex = r'^http(s)?:\/\/platform'
        return re.match(regex, string)


class JsApi(object):
    """初始化 JsApi"""
    def __init__(self, jsapi_ticket, url):
        self.sign = Sign(jsapi_ticket=jsapi_ticket)
        self.__dict__.update(self.sign.sign(url=url))

class WechatUtil(object):

    """微信工具类，可用户与微信 API 之间的交互"""

    @gen.coroutine
    def get_wxuser(self, access_token, openid):
        """用 openid 拉取用户信息
        https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140839&t=0.8130415470934214
        :return ObjectDict
        when success
        {
           "subscribe": 1,
           "openid": "o6_bmjrPTlm6_2sgVt7hMZOPfL2M",
           "nickname": "Band",
           "sex": 1,
           "language": "zh_CN",
           "city": "广州",
           "province": "广东",
           "country": "中国",
           "headimgurl":  "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4
        eMsv84eavHiaiceqxibJxCfHe/0",
          "subscribe_time": 1382694957,
          "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
          "remark": "",
          "groupid": 0,
          "tagid_list":[128,2]
        }

        when error
        {"errcode":40003,"errmsg":" invalid openid"}
        """
        response = yield self.async_http.fetch(
            wx_const.WX_INFO_USER_API % (access_token, openid))

        ret = ObjectDict(ujson.loads(response.body))
        logger.debug("[WechatUtil][get_wxuser]wxuser:{}".format(ret))
        raise gen.Return(ret)
