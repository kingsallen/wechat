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


class NoSignatureError(Exception):
    pass


class MultiDomainException(Exception):
    pass


class BaseHandler(MetaBaseHandler):
    """Handler 基类, 仅供微信端网页调用

    不要使用（创建）get_current_user()
    get_current_user() 不能为异步方法，而 parpare() 可以
    self.current_user 将在 prepare() 中以 self.current_user = XXX 的形式创建
    Refer to:
    http://www.tornadoweb.org/en/stable/web.html#other
    """

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

        # 构建 session 过程中会缓存一份当前公众号信息
        self._wechat = None
        self._qx_wechat = None
        self._unionid = None
        self._wxuser = None
        self._session_id = None
        # 处理 oauth 的 service, 会在使用时初始化
        self._oauth_service = None
        self._pass_session = None
        self._sc_cookie_id = None  # 神策设备ID

    @property
    def component_access_token(self):
        """第三方平台 component_access_token"""
        ret = self.redis.get("component_access_token", prefix=False)
        if ret is not None:
            return ret.get("component_access_token", None)
        else:
            return None

    @gen.coroutine
    def support_multi_domain(self):
        """
        WARNING: the code looks complicated, but it should be easy to understand
        return: Boolean 是否需要跳转， To 跳到那里去
        throws MultiDomainException 不应该出现的异常情况 -> 404
        settings需要添加以下：
        # **************************************************************
        settings['multi_domain'] = {}
        settings['multi_domain']['pattern'] = r"(.*).wx.dqprism.com"
        settings['multi_domain']['format'] = "{}.wx.dqprism.com"
        settings['multi_domain']['m_format'] = settings['multi_domain']['format'] + "/m"
        settings['multi_domain']['qx_appid'] = "wx1f64c12fc8f0af37"
        settings['multi_domain']['qx_domain'] = settings['multi_domain']['format'].format(settings['multi_domain']['qx_appid']) + "/recruit"
        settings['multi_domain']['help_appid'] = "wx4eb438db0b7a28cf"
        settings['multi_domain']['help_domain'] = settings['multi_domain']['format'].format(settings['multi_domain']['help_appid']) + "/h"
        settings['multi_domain']['platform'] = settings["m_host"]
        settings['m_domain'] = '.wx.dqprism.com'
        settings['platform_domain'] = settings['m_domain'] + '/m'
        settings['qx_domain'] = settings['m_domain'] + '/recruit'
        settings['helper_domain'] = settings['m_domain'] + '/h'
        settings['pass_multi_submain_host'] = ['tui-t.dqprism.com']
        # **************************************************************

        分三个环境：
        1.env=platform 企业
        如果满足appid的形式
        case #1: wx2a67d33a520ded23.wx.moseeker.com/m/path?wechat_signature=&other_param
        action: 校验signature和appid是否匹配
        如果匹配则pass
        如果不匹配则报错404

        case #2: appid.wx.moseeker.com/m/path?other_param
        action: 根据appid拉取signature, 放到params["wechat_signature"]，跳转(兼容前端需要取signature的情况)

        不满足appid的形式
        case #3: platform.moseeker.com?wechat_signature=xx&other_param
        action: 根据signature拉取appid; 跳转

        其他情况，报错

        2.env=qx 聚合号2代(待下线的项目)
        如果appid校验通过，则pass
        如果appid校验不通过，则报错
        如果是platform形式域名，则跳转(wechat_id_1_appid).wx.moseeker/dqprism.com

        3.env=help 招聘助手(待下线的项目)
        做法同env=qx
        如果appid校验通过，则pass
        如果appid校验不通过，则报错404
        如果是platform形式域名，则跳转(wechat_id_41_appid).wx.moseeker/dqprism..com

        (注:4.聚合号1代，nginx不会打到这里，不用此项目处理)
        """
        appid = ''
        multi_domain_settings = self.settings["multi_domain"]
        host = self.request.host
        multi_subdomain_match = re.match(multi_domain_settings["pattern"], host)
        if multi_subdomain_match:
            appid = multi_subdomain_match.group(1)
        signature = self.params.get("wechat_signature")
        is_platform_domain = multi_domain_settings["platform"].lower() == host.lower()

        if self.is_platform:
            # 仟寻授权完成后需要先重定向到对应的企业appid域名
            if appid == multi_domain_settings["qx_appid"]:
                wechat = yield self.wechat_ps.get_wechat(conds={"signature": signature})
                to = "https://" + multi_domain_settings["m_format"].format(wechat.appid) + self.request.uri
                return True, to
            if multi_subdomain_match and signature:  # case#1
                wechat = yield self.wechat_ps.get_wechat(conds={"signature": signature})
                if wechat.appid == appid:
                    return False, None
                else:
                    raise MultiDomainException(
                        json.dumps({"full_url": self.request.full_url(),
                                    "description": "env=platform, multi domain match, but signature and appid not match"}))
            elif multi_subdomain_match and not signature:  # case#2
                wechat = yield self.wechat_ps.get_wechat(conds={"appid": appid})
                self.params["wechat_signature"] = wechat.signature
                to = make_url(path=self.request.path, host=multi_domain_settings["m_format"].format(wechat.appid), protocol="https", params=self.params)
                return True, to
            elif is_platform_domain and signature:  # case#3
                wechat = yield self.wechat_ps.get_wechat(conds={"signature": signature})
                to = "https://" + multi_domain_settings["m_format"].format(wechat.appid) + self.request.uri
                return True, to
            elif host in settings['pass_multi_submain_host']:
                return False, None
            else:
                raise MultiDomainException(
                        json.dumps({"full_url": self.request.full_url(),
                                    "description": "env=platform, neither multidomain match nor valid platform url"}))

        elif self.is_qx:
            if multi_subdomain_match:
                if appid == multi_domain_settings["qx_appid"]:
                    return False, None
                else:
                    raise MultiDomainException(
                        json.dumps({"full_url": self.request.full_url(),
                                    "description": "env=qx, multi domain match, but appid not match settings"}))
            elif is_platform_domain:
                to = "https://" + multi_domain_settings["qx_domain"] + self.request.uri
                return True, to
            else:
                raise MultiDomainException(
                        json.dumps({"full_url": self.request.full_url(),
                                    "description": "env=qx, neither multi domain nor platform"}))

        elif self.is_help:
            if appid == multi_domain_settings["qx_appid"]:
                to = "https://" + multi_domain_settings["format"].format(settings['multi_domain']['help_appid']) + '/h' + self.request.uri
                return True, to
            if multi_subdomain_match:
                if appid == multi_domain_settings["help_appid"]:
                    return False, None
                else:
                    raise MultiDomainException(
                        json.dumps({"full_url": self.request.full_url(),
                                    "description": "env=help, is multi domain url, but appid not match help's appid"}))
            elif is_platform_domain:
                to = "https://" + multi_domain_settings["help_domain"] + self.request.uri
                return True, to
            else:
                raise MultiDomainException(
                        json.dumps({"full_url": self.request.full_url(),
                                    "description": "env=help,  neither multi domain nor platform"}))
        else:
            # 未知的特殊情况 - 理论上不应该发生
            raise MultiDomainException(
                    json.dumps({"full_url": self.request.full_url(),
                                "description": "no env matched, how could it be?"}))

    # PUBLIC API
    @check_signature
    @gen.coroutine
    def prepare(self):
        """用于生成 current_user"""

        # 支持多域名 - start *******************************
        try:
            do_redirect, to = yield self.support_multi_domain()
            self.logger.debug("[multi_submain] do_redirect:{}, to:{}".format(do_redirect, to))
            if do_redirect:
                self.redirect(to)
                return
            else:
                pass
        except MultiDomainException as mde:
            self.logger.error(mde)
            self.logger.error(traceback.format_exc())
            self.write_error(http_code=404)
        if self.request.connection.stream.closed():
            return
        # 支持多域名 - end *******************************

        yield gen.sleep(0.001)  # be nice to cpu
        ge_old0 = "wechat_signature=NmY0YWY2ZmFjMmY3OGY5M2U0YmE0MDgwZWMzMDEyZjRkNGM0YmU3OA=="
        ge_new0 = "wechat_signature=OGJiMmNlNDZmODlmMzVjOGJkNGVkODgyZDg3Zjc0NTk2OTg4OGNiMw=="
        uri = self.request.uri
        if uri.find(ge_old0) > 0:
            to_uri = "/m" + uri.replace(ge_old0, ge_new0)
            self.redirect(to_uri)
            return

        ge_old1 = "wechat_signature=NmY0YWY2ZmFjMmY3OGY5M2U0YmE0MDgwZWMzMDEyZjRkNGM0YmU3OA%3D%3D"
        ge_new1 = "wechat_signature=OGJiMmNlNDZmODlmMzVjOGJkNGVkODgyZDg3Zjc0NTk2OTg4OGNiMw=="
        uri = self.request.uri
        if uri.find(ge_old1) > 0:
            to_uri = "/m" + uri.replace(ge_old1, ge_new1)
            self.redirect(to_uri)
            return

        ge_old2 = "wechat_signature=NmY0YWY2ZmFjMmY3OGY5M2U0YmE0MDgwZWMzMDEyZjRkNGM0YmU3OA%3d%3d"
        ge_new2 = "wechat_signature=OGJiMmNlNDZmODlmMzVjOGJkNGVkODgyZDg3Zjc0NTk2OTg4OGNiMw=="
        uri = self.request.uri
        if uri.find(ge_old2) > 0:
            to_uri = "/m" + uri.replace(ge_old2, ge_new2)
            self.redirect(to_uri)
            return

        # 构建 session 之前先缓存一份 wechat
        self._wechat = yield self._get_current_wechat()
        if self.request.connection.stream.closed():
            return

        self._qx_wechat = yield self._get_qx_wechat()
        if not self._wechat:
            self._wechat = self._qx_wechat

        # 初始化 oauth service
        self._oauth_service = WeChatOauth2Service(
            self._wechat, self.fullurl(), self.component_access_token)

        self._pass_session = PassportCache()

        # 如果有 code，说明刚刚从微信 oauth 回来
        code = self.params.get("code")
        state = self.params.get("state")

        self.logger.debug("+++++++++++++++++START OAUTH+++++++++++++++++++++")
        self.logger.debug(
            "[prepare]code:{}, state:{}, request_url:{} ".format(
                code, state, self.request.uri))
        # 预设神策分析全局属性
        conds = {'id': self._wechat.company_id}
        company = yield self.company_ps.get_company(conds=conds, need_conf=True)
        self.sa.register_super_properties(ObjectDict({"companyId": company.id,
                                                      "companyName": company.abbreviation}))

        # 获取神策设备ID
        self._get_sc_cookie_id()
        # 添加joywok js config等环境变量
        yield self._get_client_env_config()

        if self.in_wechat:
            # 用户同意授权
            if code and self._verify_code(code):
                # 保存 code 进 cookie
                self.set_cookie(
                    const.COOKIE_CODE,
                    to_str(code),
                    expires_days=1,
                    httponly=True)

                # 来自 qx 的授权, 获得 userinfo
                if state == wx_const.WX_OAUTH_DEFAULT_STATE:
                    self.logger.debug("来自 qx 的授权, 获得 userinfo")
                    userinfo = yield self._get_user_info(code, is_qx=True)
                    if userinfo:
                        self.logger.debug("来自 qx 的授权, 获得 userinfo:{}".format(userinfo))
                        yield self._handle_user_info(userinfo)
                    else:
                        self.logger.debug("来自 qx 的 code 无效")

                # 来自企业号，招聘助手的静默授权
                else:
                    self.logger.debug("来自企业号的静默授权")
                    self._unionid = from_hex(state)
                    openid = yield self._get_user_openid(code)
                    if openid:
                        self.logger.debug("来自企业号的静默授权, openid:{}".format(openid))
                        self._wxuser = yield self._handle_ent_openid(
                            openid, self._unionid)
                        self.logger.info("来自企业号的静默授权, openid:{}, _unionid:{}".format(openid, self._unionid))
                    else:
                        self.logger.debug("来自企业号的 code 无效")

            elif state:  # 用户拒绝授权
                # TODO 拒绝授权用户，是否让其继续操作? or return
                pass
        else:
            # pc端授权
            if code and self._verify_code(code):
                self.set_cookie(
                    const.COOKIE_CODE,
                    to_str(code),
                    expires_days=1,
                    httponly=True)
                userinfo = yield self._get_user_info_pc(code)
                if userinfo:
                    self.logger.debug("来自 pc 的授权, 获得 userinfo:{}".format(userinfo))
                    yield self._handle_user_info(userinfo)
                else:
                    self.logger.debug("来自 pc 的 code 无效")

        # 构造并拼装 session
        yield self._fetch_session()
        if self.request.connection.stream.closed():
            return

        # joywok取消员工身份时，清除session，重新认证
        yield self._update_joywok_employee_session()

        # 设置神策用户属性
        if self.current_user.employee:
            user_role = 1
            company_id = self.current_user.company.id
            company_name = self.current_user.company.abbreviation
        else:
            user_role = 0
            company_id = 0
            company_name = ''
            #企业微信判断有效员工
            if self.in_workwx:
                is_subscribe = yield self.position_ps.get_hr_wx_user(self.current_user.sysuser.unionid, self._wechat.id)
                if is_subscribe:
                    # 如果已经关注公众号，无需跳转微信，可生成员工信息之后访问主页
                    yield self.workwx_ps.employee_bind(self.current_user.sysuser.unionid, self._wechat.company_id)
                else:
                    #如果没有关注公众号，跳转微信
                    workwx_user_record = yield self.workwx_ps.get_workwx_user_by_sysuser_id(self.current_user.sysuser.id, self._wechat.company_id)
                    if workwx_user_record:
                        workwx_fivesec_url = self.make_url(path.WOKWX_FIVESEC_PAGE, self.params) + "&workwx_userid={}&company_id={}".format(workwx_user_record.userid, self._wechat.company_id)
                        self.redirect(workwx_fivesec_url)
                        return
                    else:
                        url = self.make_url(path.WOKWX_OAUTH_PAGE, self.params)
                        yield self.redirect(url)
                        return

        _, profile = yield self.profile_ps.has_profile(self.current_user.sysuser.id if self.current_user.sysuser else 0)
        profiles = {
            'user_role': user_role,
            'sysuser_id': self.current_user.sysuser.id if self.current_user.sysuser else self._sc_cookie_id,
            'company_id': company_id,
            'company_name': company_name,
            'ProfileCompleteness': profile.basic.completeness if profile and profile.basic else 0
        }
        self.profile_set(profiles=profiles)

        # 构造 access_time cookie
        self._set_access_time_cookie()

        # 构造 mviewer_id
        self._make_moseeker_viewer_id()

        # 内存优化
        self._wechat = None
        self._qx_wechat = None
        self._unionid = None
        self._wxuser = None
        self._qxuser = None
        self._session_id = None

        self.logger.debug("current_user:{}".format(self.current_user))
        self.logger.debug("+++++++++++++++++PREPARE OVER+++++++++++++++++++++")

    # PROTECTED
    @gen.coroutine
    def _handle_user_info(self, userinfo):
        """
        根据 unionid 创建 user_user 如果存在则不创建， 返回 user_id
        创建 聚合号 wxuser，绑定刚刚创建的 user_id
        静默授权企业号, state 为 unionid

        userinfo 结构：
        ObjectDict(
        "openid":" OPENID",
        "nickname": NICKNAME,
        "sex":"1",
        "province":"PROVINCE"
        "city":"CITY",
        "country":"COUNTRY",
        "headimgurl":    "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx",
        "privilege":["PRIVILEGE1", "PRIVILEGE2"],
        "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        )
        """
        self._unionid = userinfo.unionid
        if self.is_platform:
            source = const.WECHAT_REGISTER_SOURCE_PLATFORM
        else:
            source = const.WECHAT_REGISTER_SOURCE_QX

        # 创建 user_user
        user_id = yield self.user_ps.create_user_user(
            userinfo,
            wechat_id=self._wechat.id,
            remote_ip=self.request.remote_ip,
            source=source)

        if user_id:
            self._log_customs.update(new_user=const.YES)

        self.logger.debug("[_handle_user_info]user_id: {}".format(user_id))

        user = yield self.user_ps.get_user_user({
            "unionid":  userinfo.unionid,
            "parentid": 0  # 保证查找正常的 user record
        })

        # 神策数据关联：如果用户已绑定手机号，对用户做注册
        if bool(user.username.isdigit()):
            self.logger.debug("[sensors_signup_oauth]ret_user_id: {}, origin_user_id: {}".format(user_id,
                                                                                                 self._sc_cookie_id))
            self.sa.track_signup(user_id, self._sc_cookie_id or user_id)

        self.track('cWxAuth', properties={'origin': source}, distinct_id=user_id, is_login_id=True if bool(user.username.isdigit()) else False)
        # 设置用户首次授权时间
        self.profile_set(profiles={'first_oauth_time': user.register_time}, distinct_id=user_id, is_login_id=True, once=True)

        # 创建 qx 的 user_wx_user
        yield self.user_ps.create_qx_wxuser_by_userinfo(userinfo, user_id)

        # 静默授权时同步将用户信息，更新到qxuser和user_user
        yield self._sync_userinfo(self._unionid, userinfo)

        if not self._authable(self._wechat.type):
            # 该企业号是订阅号 则无法获得当前 wxuser 信息, 无需静默授权
            self._wxuser = ObjectDict()

    @gen.coroutine
    def _update_joywok_employee_session(self):
        if self._client_env == const.CLIENT_JOYWOK and not self.current_user.employee:
            self._pass_session.clear_session(self._session_id, self._wechat.id)
            url = self.make_url(path.JOYWOK_HOME_PAGE)
            yield self.redirect(url)

    @gen.coroutine
    def _get_client_env_config(self):
        client_env = ObjectDict({"name": self._client_env})
        if self._client_env == const.CLIENT_JOYWOK:
            headers = ObjectDict({"Referer": self.request.full_url()})
            res = yield self.joywok_ps.get_joywok_info(appid=settings['joywok_appid'],
                                                       method=const.JMIS_SIGNATURE,
                                                       headers=headers)
            client_env.update({
                "args": ObjectDict({
                    "appid": res.app_id,
                    "signature": res.signature,
                    "timestamp": res.timestamp,
                    "nonceStr": res.nonce,
                    "corpid": res.corp_id,
                    "redirect_url": res.redirect_url})
            })
        self.namespace = {"client_env": client_env}

    @gen.coroutine
    def _handle_ent_openid(self, openid, unionid):
        """根据企业号 openid 和 unionid 创建企业号微信用户"""
        wxuser = None
        if self.is_platform or self.is_help:
            wxuser = yield self.user_ps.create_user_wx_user_ent(
                openid, unionid, self._wechat.id)
        raise gen.Return(wxuser)

    @gen.coroutine
    def _sync_userinfo(self, unionid, userinfo):
        """静默授权时同步将用户信息，更新到qxuser和user_user"""
        # todo(niuzhenya@moseeker.com) 此处更新没有将所有wxuser的wxinfo都做更新，原因：wxuser的info没有展示的地方，展示目前都用的是user_user的info;
        # todo 过多的冗余字段，可以考虑在后期将数据库的结构优化
        yield self.user_ps.update_user_wx_info(unionid, userinfo)
        # yield self.user_ps.update_wxuser_wx_info(unionid, userinfo)

    def _authable(self, wechat_type):
        """返回当前公众号是否可以 OAuth

        服务号有网页 OAuth 权限
        订阅号没有网页 OAuth 权限
        https://mp.weixin.qq.com/wiki/7/2d301d4b757dedc333b9a9854b457b47.html
        """

        if wechat_type is None:
            return False
        return wechat_type is const.WECHAT_TYPE_SERVICE

    def _verify_code(self, code):
        """检查 code 是不是之前使用过的"""

        old = self.get_cookie(const.COOKIE_CODE)

        if not old:
            return True
        return str(old) != str(code)

    @gen.coroutine
    def _get_current_wechat(self, qx=False):
        if qx:
            signature = self.settings['qx_signature']
        else:
            if self.is_platform:
                signature = self.params['wechat_signature']
            elif self.is_qx:
                signature = self.settings['qx_signature']
            elif self.is_help:
                signature = self.settings['helper_signature']
            else:
                self.logger.error("wechat_signature missing")
                raise NoSignatureError()

        wechat = yield self.wechat_ps.get_wechat(conds={
            "signature": signature
        })
        if not wechat:
            self.write_error(http_code=404)
            return

        raise gen.Return(wechat)

    @gen.coroutine
    def _get_qx_wechat(self):
        wechat = yield self._get_current_wechat(qx=True)
        raise gen.Return(wechat)

    @gen.coroutine
    def _get_user_info(self, code, is_qx=False):
        if is_qx:
            self._oauth_service.wechat = self._qx_wechat
        else:
            self._oauth_service.wechat = self._wechat
        try:
            userinfo = yield self._oauth_service.get_userinfo_by_code(code)
            raise gen.Return(userinfo)
        except WeChatOauthError as e:
            raise gen.Return(None)

    @gen.coroutine
    def _get_user_info_pc(self, code):
        try:
            userinfo = yield self._oauth_service.get_userinfo_by_code_pc(code)
            raise gen.Return(userinfo)
        except WeChatOauthError as e:
            raise gen.Return(None)

    @gen.coroutine
    def _get_user_openid(self, code):
        self._oauth_service.wechat = self._wechat
        try:
            openid, _ = yield self._oauth_service.get_openid_unionid_by_code(
                code)
            raise gen.Return(openid)
        except WeChatOauthError as e:
            raise gen.Return(None)

    @gen.coroutine
    def _fetch_session(self):
        """尝试获取 session 并创建 current_user，如果获取失败走 oauth 流程"""
        ok = False
        self._session_id = to_str(
            self.get_secure_cookie(
                const.COOKIE_SESSIONID))

        if self._session_id:
            if self.is_platform or self.is_help:
                # 判断是否可以通过 session，直接获得用户信息，这样就不用跳授权页面
                ok = yield self._get_session_by_wechat_id(self._session_id, self._wechat.id)
                if not ok:
                    ok = yield self._get_session_by_wechat_id(self._session_id, self.settings['qx_wechat_id'])
            elif self.is_qx:
                ok = yield self._get_session_by_wechat_id(self._session_id, self.settings['qx_wechat_id'])

            need_oauth = not ok

        else:
            need_oauth = True
            if self._client_env == const.CLIENT_JOYWOK:
                url = self.make_url(path.JOYWOK_HOME_PAGE)
                yield self.redirect(url)
            elif self._client_env == const.CLIENT_WORKWX:
                url = self.make_url(path.WOKWX_OAUTH_PAGE, self.params)
                yield self.redirect(url)

        if need_oauth:
            if self.in_wechat and not self._unionid:
                # unionid 不存在，则进行仟寻授权
                self._oauth_service.wechat = self._qx_wechat
                # 仟寻授权需要重定向到仟寻appid对应的域名
                self._get_oauth_redirect_url()
                url = self._oauth_service.get_oauth_code_userinfo_url()
                self.logger.debug("qx_oauth_redirect_url: {}".format(url))
                self.redirect(url)
                return
            else:
                yield self._build_session()

                # GA 需求：
                # 在 current_user 中添加 has_profile flag
                # 在企业微信端页面，现有代码的  ga('send', 'pageview’) 前，
                # 判断如果该页是用户该session登陆后（主动或者被动都可以）访问的第一个页面的话，
                # 插入以下语句：
                # ga('set', 'userId', ‘XXXXXX’);
                # ga('set', 'dimension2', 'YYYYY’);
                # ga('set', 'dimension3', 'ZZZZZZ’);

                # if self.current_user.sysuser:
                #     result, profile = yield self.profile_ps.has_profile(self.current_user.sysuser.id)
                #     self.current_user.has_profile = result

    def _get_oauth_redirect_url(self):
        # 仟寻授权需要重定向到仟寻appid对应的域名
        if self.is_help:
            host_suffix = "/h"
        elif self.is_qx:
            host_suffix = "/recruit"
        else:
            host_suffix = "/m"
        self._oauth_service.redirect_url = "https://" + settings['multi_domain']['format'].format(
            settings['multi_domain']['qx_appid']) + host_suffix + self.request.uri

    @gen.coroutine
    def _build_session(self):
        """用户确认向仟寻授权后的处理，构建 session"""

        self.logger.debug("_build_session start")

        session = ObjectDict()
        session.wechat = self._wechat

        # 该 session 只做首次仟寻登录查找各关联帐号所用(微信环境内)
        if self._unionid:
            # 只对微信 oauth 用户创建qx session
            session.qxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                unionid=self._unionid,
                wechat_id=self.settings['qx_wechat_id'],
                fields=['id', 'unionid', 'sysuser_id']
            )
            self._session_id = self._make_new_session_id(
                session.qxuser.sysuser_id)
            self.logger.info("session_id:{}-----unionid:{}".format(self._session_id, self._unionid))
            self._pass_session.save_qx_sessions(
                self._session_id, session.qxuser)
            self.set_secure_cookie(
                const.COOKIE_SESSIONID,
                self._session_id,
                httponly=True,
                domain=settings['root_host']
            )

        # 重置 wxuser，qxuser，构建完整的 session
        self._wxuser = ObjectDict()
        self._qxuser = ObjectDict()
        yield self._build_session_by_unionid(self._unionid)

    @gen.coroutine
    def _get_session_by_wechat_id(self, session_id, wechat_id):
        """尝试获取 session"""

        key = const.SESSION_USER.format(session_id, wechat_id)
        value = self.redis.get(key)
        self.logger.debug(
            "_get_session_by_wechat_id redis wechat_id:{} session: {}, key: {}".format(
                wechat_id, value, key))
        if value:
            # 如果有 value， 返回该 value 作为 self.current_user
            session = ObjectDict(value)
            self._unionid = session.qxuser.unionid
            self._wxuser = session.wxuser
            self._qxuser = session.qxuser
            yield self._build_session_by_unionid(self._unionid)
            raise gen.Return(True)

        raise gen.Return(False)

    @gen.coroutine
    def _build_session_by_unionid(self, unionid):
        """从 unionid 构建 session"""

        session = ObjectDict()
        # session_id = to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        if not unionid:
            # 非微信环境, 忽略 wxuser, qxuser
            session.wxuser = ObjectDict()
            session.qxuser = ObjectDict()
        else:
            session.wxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                unionid=unionid, wechat_id=self._wechat.id)
            session.qxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                unionid=unionid, wechat_id=self.settings['qx_wechat_id'])

        if not self._session_id:
            self._session_id = self._make_new_session_id(
                session.qxuser.sysuser_id)
            self.set_secure_cookie(
                const.COOKIE_SESSIONID,
                self._session_id,
                httponly=True,
                domain=settings['root_host'])

        if self.is_platform:
            self._pass_session.save_ent_sessions(
                self._session_id, session, self._wechat.id)

        yield self._add_sysuser_to_session(session, self._session_id)
        session.sc_cookie_id = self._sc_cookie_id

        session.wechat = self._wechat
        self._add_jsapi_to_wechat(session.wechat)

        yield self._add_company_info_to_session(session)
        if self.is_platform and self.params.recom:
            yield self._add_recom_to_session(session)

        self.current_user = session

    @gen.coroutine
    def _add_company_info_to_session(self, session):
        """拼装 session 中的 company, employee
        """

        session.company = yield self._get_current_company(session.wechat.company_id)

        if session.sysuser.id and self.is_platform:
            employee = yield self.user_ps.get_valid_employee_by_user_id(
                user_id=session.sysuser.id, company_id=session.company.id)
            session.employee = employee

    @gen.coroutine
    def _get_current_company(self, company_id):
        """获得企业母公司信息"""

        conds = {'id': company_id}
        company = yield self.company_ps.get_company(conds=conds, need_conf=True)

        # 配色处理，如果theme_id为5表示公司使用默认配置，不需要将原始配色信息传给前端
        # 如果将theme_id为5的传给前端，会导致前端颜色无法正常显示默认颜色
        if company.conf_theme_id != 5 and company.conf_theme_id:
            theme = yield self.wechat_ps.get_wechat_theme(
                {'id': company.conf_theme_id, 'disable': 0})
            if theme:
                company.update({
                    'theme': [
                        theme.background_color,
                        theme.title_color,
                        theme.button_color,
                        theme.other_color
                    ]
                })
        else:
            company.update({'theme': None})

        raise gen.Return(company)

    @gen.coroutine
    def _add_recom_to_session(self, session):
        """拼装 session 中的 recom"""

        recom_user_id = decode_id(self.params.recom)
        recom = yield self.user_ps.get_user_user({
            "id": recom_user_id
        })
        if recom:
            recom_wxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                unionid=recom.unionid, wechat_id=self._wechat.id)
            recom.openid = recom_wxuser.openid
            recom.wxuser_id = recom_wxuser.id

        session.recom = recom

    @gen.coroutine
    def _add_sysuser_to_session(self, session, session_id):
        """拼装 session 中的 sysuser"""

        user_id = match_session_id(session_id)
        sysuser = yield self.user_ps.get_user_user({
            "id": user_id
        })

        if sysuser.parentid and sysuser.parentid > 0:
            sysuser = yield self.user_ps.get_user_user({
                "id": sysuser.parentid
            })
            self.clear_cookie(name=const.COOKIE_SESSIONID)

        if sysuser:
            sysuser = self.user_ps.adjust_sysuser(sysuser)

        # 对于非微信环境，用户登录后，如果帐号已经绑定微信，则同时获取微信用户信息
        if sysuser.unionid and not session.qxuser:
            session.qxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                unionid=sysuser.unionid, wechat_id=self.settings['qx_wechat_id'])

        session.sysuser = sysuser

    def _get_sc_cookie_id(self):
        """获取神策设备ID"""
        sc_cookie_name = const.SENSORS_COOKIE
        sc_cookie = unquote(self.get_cookie(sc_cookie_name) or '{}')
        self.logger.debug("sc_cookie: {}".format(sc_cookie))
        sc_cookie = ObjectDict(json.loads(sc_cookie))
        self._sc_cookie_id = sc_cookie.distinct_id

    def _add_jsapi_to_wechat(self, wechat):
        """拼装 jsapi"""
        wechat.jsapi = JsApi(
            jsapi_ticket=wechat.jsapi_ticket,
            url=self.fullurl(encode=False))

    def _make_new_session_id(self, user_id):
        """创建新的 session_id

        redis 中 session 的 key 的格式为 session_id_<wechat_id>
        创建的 session_id 保证唯一
        session_id 目前本身不做持久化，仅仅保存在 redis 中
        后续是否需要做持久化待讨论
        :return: session_id
        """
        while True:
            session_id = const.SESSION_ID.format(
                str(user_id),
                sha1(os.urandom(24)).hexdigest())
            record = self.redis.exists(session_id + "_*")
            if record:
                continue
            else:
                return session_id

    def _make_moseeker_viewer_id(self):
        """创建新的mviewer_id
        不论是登录，或非登录用户，都会有唯一的 mviewer_id，标识独立的用户。
        主要用于日志统计中 UV 的统计
        """

        def _make_new_moseeker_viewer_id():

            while True:
                mviewer_id = const.MVIEWER_ID.format(
                    "_",
                    sha1(os.urandom(24)).hexdigest())
                return mviewer_id

        # 登录，或非登录用户（非微信环境），都需要创建 mviewer_id
        mviewer_id = to_str(self.get_secure_cookie(const.COOKIE_MVIEWERID))
        if not mviewer_id:
            mviewer_id = _make_new_moseeker_viewer_id()
            self.set_secure_cookie(
                const.COOKIE_MVIEWERID,
                mviewer_id,
                httponly=True)

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        # TODO 添加前端 url 的白名单参数
        add_namespace = ObjectDict(
            env=self.env,
            params=self.params,
            make_url=self.make_url,
            const=const,
            path=path,
            static_url=self.static_url,
            current_user=self.current_user,
            settings=self.settings
        )
        namespace.update(add_namespace)
        return namespace

    def _set_access_time_cookie(self):
        """设置 _ac cookie 表示该session首次访问页面时间
        使用 unix 时间戳
        https://timanovsky.wordpress.com/2009/04/09/get-unix-timestamp-in-java-python-erlang/
        """
        cookie_name = '_ac'
        if not self.get_cookie(cookie_name):
            unix_time_stamp = str(int(time.time()))
            self.set_cookie(cookie_name, unix_time_stamp)

    def make_url(self, path, params=None, host="", protocol="https", escape=None, **kwargs):
        """
        host 环境不能直接从 request 中获取，需要根据环境确定
        :param path:
        :param host:
        :param params:
        :param protocol:
        :param escape:
        :param kwargs:
        :return:
        """
        if not host:
            host = self.host
        return make_url(path, params, host, protocol, escape, **kwargs)

    def fullurl(self, encode=True):
        """
        获取当前 url， 默认删除 query 中的 code 和 state。

        和 oauth 有关的 参数会影响 prepare 方法
        :param encode: False，不会 Encode，主要用在生成 jdsdk signature 时使用
        :return:
        """

        full_url = to_str(self.request.full_url())

        if not self.host in self.request.full_url():
            full_url = full_url.replace(self.settings.m_host, self.host)

        if not self.domain in self.request.full_url():
            full_url = full_url.replace(self.settings.m_domain, self.domain)

        if not encode:
            return full_url
        return url_subtract_query(full_url, ['code', 'state'])

    def redirect_to_route(self, route_name, params, *args):
        route_url = self.reverse_url(route_name, *args)
        to = self.make_url(route_url, params)
        self.redirect(to)

    def get_user_locale(self):
        """如果公司设置了语言，以公司设置为准，
        否则判断ua的language，
        最后fallback到setting中的默认配置"""

        # 如果没有当前公司，那么使用默认locale
        if not self.current_user or not self.current_user.company:
            return None

        display_locale = self.current_user.company.conf_display_locale
        if display_locale:
            return locale.get(display_locale)
        else:
            useragent = self.request.headers.get('User-Agent')
            lang_from_ua = languge_code_from_ua(useragent)

            lang = lang_from_ua or settings['default_locale']
            return locale.get(lang)

    def track(self, event, properties=None, distinct_id=0, is_login_id=False):
        """神策埋点"""
        try:
            if not properties:
                properties = ObjectDict()
            distinct_id, is_login_id = self._get_distinct_id_and_is_login_id(distinct_id, is_login_id)
            if distinct_id:
                properties.update(reqTime=curr_now(),
                                  isEmployee=bool(self.current_user.employee if self.current_user else None),
                                  sendTime=self.params.send_time if self.params else None)
                self.logger.debug('[sensors_track] distinct_id:{}, event_name: {}, properties: {}, is_login_id: {}'.format(
                    distinct_id, event, properties, is_login_id))
                self.sa.track(distinct_id=distinct_id,
                              event_name=event,
                              properties=properties,
                              is_login_id=is_login_id)
            else:
                self.logger.debug('[sensors_no_user_id] event_name: {}, properties: {}'.format(event, properties))
        except Exception as e:
            self.logger.error('[sensors_track_exception] distinct_id: {}, event_name: {}, properties: {}, is_login_id: {}, error_track: {}'.format(
                self.current_user.sysuser.id or self.current_user.sc_cookie_id, event, properties, True if self.current_user.sysuser.id else False,
                traceback.format_exc()))

    def profile_set(self, profiles, distinct_id=0, is_login_id=False, once=False):
        """设置用户属性"""
        try:
            distinct_id, is_login_id = self._get_distinct_id_and_is_login_id(distinct_id, is_login_id)
            if distinct_id:
                self.logger.debug('[sensors_profile_set] distinct_id:{}, profiles: {}, is_login_id: {}'.format(
                    distinct_id, profiles, is_login_id))
                if once:
                    self.sa.profile_set_once(distinct_id=distinct_id,
                                             profiles=profiles,
                                             is_login_id=is_login_id)
                else:
                    self.sa.profile_set(distinct_id=distinct_id,
                                        profiles=profiles,
                                        is_login_id=is_login_id)
            else:
                self.logger.debug('[profile_set_sensors_no_user_id] profiles: {}'.format(profiles))
        except Exception as e:
            self.logger.error('[sensors_profile_set_exception] distinct_id: {}, profiles: {}, is_login_id: {}, error_track: {}'.format(
                self.current_user.sysuser.id or self.current_user.sc_cookie_id, profiles, True if self.current_user.sysuser.id else False,
                traceback.format_exc()))

    def _get_distinct_id_and_is_login_id(self, distinct_id=0, is_login_id=False):
        """获取distinct_id、is_login_id的值，distinct_id默认值当前用户id，is_login_id默认值为当前用户是否验证过手机号"""
        if distinct_id:
            is_login_id = is_login_id
        elif self.current_user.sysuser:
            is_login_id = True if self.current_user.sysuser.mobileverified else False
        distinct_id = distinct_id or (
            self.current_user.sysuser.id if self.current_user.sysuser else 0) or self.current_user.sc_cookie_id or 0
        return distinct_id, is_login_id

    def get_current_locale(self):
        """如果公司设置了语言，以公司设置为准，
        否则判断ua的language，返回language"""
        if not self.current_user or not self.current_user.company or not self.current_user.company.conf_display_locale:
            useragent = self.request.headers.get('User-Agent')
            display_locale = languge_code_from_ua(useragent)
        elif self.current_user.company.conf_display_locale:
            display_locale = self.current_user.company.conf_display_locale
        else:
            display_locale = None
        return display_locale
