# coding=utf-8

from urllib.parse import quote
import tornado.gen as gen

import conf.wechat as wx_const

from util.common.sign import Sign
from util.tool.http_tool import http_get

from globals import logger
from setting import settings
from service.page.thirdparty.workwx import WorkwxPageService


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
    def get_openid_unionid_by_code_pc(self, code):
        """根据code尝试获取openid"""
        access_token_info = yield self._get_access_token_by_code(code, pc=True)
        if access_token_info.errcode:
            raise WeChatOauthError("get_openid_unionid_by_code: {}".format(access_token_info.errmsg))
        else:
            openid = access_token_info.get('openid')
            # 缓存 access_token
            self._access_token = access_token_info.get('access_token')
        raise gen.Return(openid)

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

    @gen.coroutine
    def get_userinfo_by_code_pc(self, code):
        """根据 code 尝试获取 userinfo
        :param code:
        :return:
        """
        openid = yield self.get_openid_unionid_by_code_pc(code)
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

    def _get_access_token_url(self, code, pc=None):
        """生成获取 access_token 的 url"""
        if pc is True:
            url = (wx_const.WX_OAUTH_GET_ACCESS_TOKEN % (
                settings['open_app_id'],
                settings['open_secret'],
                code
            ))
        elif self.wechat.third_oauth:
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
    def _get_access_token_by_code(self, code, pc=None):
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
        ret = yield http_get(self._get_access_token_url(code, pc=pc), infra=False)
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
        if ret.headimgurl and "http:" in ret.headimgurl:
            ret.headimgurl = ret.headimgurl.replace("http:", "https:", 1)
        raise gen.Return(ret)


class JsApi(object):
    """初始化 JsApi"""
    def __init__(self, jsapi_ticket, url):
        self.sign = Sign(jsapi_ticket=jsapi_ticket)
        self.__dict__.update(self.sign.sign(url=url))


class WorkWXOauth2Service(WeChatOauth2Service):
    """ 企业微信 OAuth 2.0 实现

    refer to:
    https://work.weixin.qq.com/api/doc#90000/90135/91020
    """

    def __init__(self, workwx, redirect_url):
        self.redirect_url = redirect_url
        self.workwx = workwx
        self.state = 0

        # 缓存 access_token
        self._access_token = None

    def _get_oauth_code_url(self, is_base=1):
        """生成获取 code 的 url, oauth的url 跟微信是一样的
        """
        oauth_url = wx_const.WX_OAUTH_GET_CODE % (
            self.workwx.corpid,
            quote(self.redirect_url),
            self._get_oauth_type(is_base),
            self.state)
        logger.debug("get_code_url: {0}".format(oauth_url))
        return oauth_url

    @gen.coroutine
    def get_userinfo_by_code(self, code, company):
        """根据 code 尝试获取 userinfo
        :param code:
        :return:
        """
        # access_token = yield self._get_access_token_by_corpid()
        self._access_token = self.workwx.access_token
        user_id = yield self._get_userid_by_code(code, company)
        if user_id.get('OpenId') and not user_id.get('UserId'):  # a企业员A工转发给B,B不是a企业员工，B可以访问三个页面，其他提醒去微信打开
            userinfo = "referral-non-employee"
        else:
            user_id = user_id.get('UserId')
            userinfo = yield self._get_userinfo_by_userid(user_id, company)
            department_names = yield self._get_departments_by_deptids(userinfo.get('department'), company)
            userinfo.update({"department_name_list": department_names})
        raise gen.Return(userinfo)

    @gen.coroutine
    def _get_userid_by_code(self, code, company):
        """用 code和access_token 拉取UserId
        :return ObjectDict
        when success
        {
           "errcode": 0,
           "errmsg": "ok",
           "UserId":"USERID",
           "DeviceId":"DEVICEID"
        }

        when error
        {"errcode":40003,"errmsg":" invalid openid"}
        """
        ret = yield http_get(wx_const.WORKWX_OAUTH_GET_USERID % (self._access_token, code), infra=False)
        if int(ret.errcode) in [42001, 40014]:
            yield self._refresh_workwx_access_token(company)
            ret = yield http_get(wx_const.WORKWX_OAUTH_GET_USERID % (self._access_token, code), infra=False)

        raise gen.Return(ret)

    @gen.coroutine
    def _get_userinfo_by_userid(self, user_id, company):
        """用 UserId 拉取用户信息
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
        ret = yield http_get(wx_const.WORKWX_OAUTH_GET_USERINFO % (self._access_token, user_id), infra=False)
        if int(ret.errcode) in [42001, 40014]:
            yield self._refresh_workwx_access_token(company)
            ret = yield http_get(wx_const.WORKWX_OAUTH_GET_USERINFO % (self._access_token, user_id), infra=False)
        if ret.avatar and "http:" in ret.avatar:
            ret.avatar = ret.avatar.replace("http:", "https:", 1)
        raise gen.Return(ret)

    @gen.coroutine
    def _get_departments_by_deptids(self, department_ids, company):
        """用 department_id 拉取部门名称
        :return ObjectDict
        when success
        {
           "id": 2,
           "name": "广州研发中心",
           "parentid": 1,
           "order": 10
       }
        when error
        {"errcode": ,"errmsg":" invalid access_token"}
        """
        department_names = []
        for department_id in department_ids:
            ret = yield http_get(wx_const.WORKWX_OAUTH_GET_DEPARTMENT % (self._access_token, department_id), infra=False)
            if int(ret.errcode) in [42001, 40014]:
                yield self._refresh_workwx_access_token(company)
                ret = yield http_get(wx_const.WORKWX_OAUTH_GET_DEPARTMENT % (self._access_token, department_id),infra=False)
            departments = ret.get("department")
            for department_info in departments:
                if department_info.get("id") == department_id:
                    department_names.append(department_info.get("name"))
        raise gen.Return(department_names)

    @gen.coroutine
    def _refresh_workwx_access_token(self, company):

        workwx_ps = WorkwxPageService()
        yield workwx_ps.refresh_workwx_access_token(self.workwx.company_id)  # 如果access_token失效，刷新access_token
        self.workwx = yield workwx_ps.get_workwx(self.workwx.company_id, company.hraccount_id)
        self._access_token = self.workwx.access_token
