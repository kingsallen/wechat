# coding=utf-8

# Copyright 2016 MoSeeker

import os
import re
from hashlib import sha1
from tornado import gen

import conf.common as const
import conf.wechat as wx_const
import conf.path as path

from handler.metabase import MetaBaseHandler
from oauth.wechat import WeChatOauth2Service, WeChatOauthError, JsApi
from util.common import ObjectDict
from util.common.cipher import decode_id
from util.common.decorator import check_signature
from util.tool.str_tool import to_str, to_bytes, from_hex
from util.tool.url_tool import url_subtract_query, make_url


class NoSignatureError(Exception):
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
        # 处理 oauth 的 service, 会在使用时初始化
        self._oauth_service = None

    @property
    def fullurl(self):
        """获取当前 url， 默认删除 query 中的 code 和 state。

        和 oauth 有关的 参数会影响 prepare 方法
        """
        return url_subtract_query(self.request.full_url(), ['code', 'state'])

    @property
    def component_access_token(self):
        """第三方平台 component_access_token"""
        ret = self.redis.get("component_access_token", prefix=False)
        if ret is not None:
            return ret.get("component_access_token", None)
        else:
            return None

    # PUBLIC API
    @check_signature
    @gen.coroutine
    def prepare(self):
        """用于生成 current_user"""

        # 构建 session 之前先缓存一份 wechat
        self._wechat = yield self._get_current_wechat()
        self._qx_wechat = yield self._get_qx_wechat()

        # 初始化 oauth service
        self._oauth_service = WeChatOauth2Service(
            self._wechat, self.fullurl, self.component_access_token)

        # 如果有 code，说明刚刚从微信 oauth 回来
        code = self.params.get("code")
        state = self.params.get("state")

        self.logger.debug("+++++++++++++++++START OAUTH+++++++++++++++++++++")
        self.logger.debug("[prepare]code:{}, state:{}, request_url:{} ".format(code, state, self.request.uri))

        if self.in_wechat:
            # 用户同意授权
            if code and self._verify_code(code):
                # 保存 code 进 cookie
                self.set_cookie(const.COOKIE_CODE, to_str(code), expires_days=1, httponly=True)

                # 来自 qx 的授权, 获得 userinfo
                if state == wx_const.WX_OAUTH_DEFAULT_STATE:
                    self.logger.debug("来自 qx 的授权, 获得 userinfo")
                    userinfo = yield self._get_user_info(code)
                    self.logger.debug("来自 qx 的授权, 获得 userinfo:{}".format(userinfo))
                    yield self._handle_user_info(userinfo)

                # 来自企业号的静默授权
                else:
                    self.logger.debug("来自企业号的静默授权")
                    self._unionid = from_hex(state)
                    openid = yield self._get_user_openid(code)
                    self.logger.debug("来自企业号的静默授权, openid:{}".format(openid))
                    self._wxuser = yield self._handle_ent_openid(
                        openid, self._unionid)

            elif state:  # 用户拒绝授权
                # TODO 拒绝授权用户，是否让其继续操作? or return
                pass

        # 构造并拼装 session
        yield self._fetch_session()

        # 内存优化
        self._wechat = None
        self._qx_wechat = None
        self._unionid = None
        self._wxuser = None
        self._qxuser = None

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
        self.logger.debug("[_handle_user_info]userinfo: {}".format(userinfo))

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

        self.logger.debug("[_handle_user_info]user_id: {}".format(user_id))

        # 创建 qx 的 user_wx_user
        yield self.user_ps.create_qx_wxuser_by_userinfo(userinfo, user_id)

        if not self._authable():
            # 该企业号是订阅号 则无法获得当前 wxuser 信息, 无需静默授权
            self._wxuser = ObjectDict()

    @gen.coroutine
    def _handle_ent_openid(self, openid, unionid):
        """根据企业号 openid 和 unionid 创建企业号微信用户"""
        wxuser = None
        if self.is_platform:
            wxuser = yield self.user_ps.create_user_wx_user_ent(
                openid, unionid, self._wechat.id)
            self.logger.debug("_handle_ent_openid, wxuser:{}".format(wxuser))
        raise gen.Return(wxuser)

    def _authable(self):
        """返回当前公众号是否可以 OAuth

        服务号有网页 OAuth 权限
        订阅号没有网页 OAuth 权限
        https://mp.weixin.qq.com/wiki/7/2d301d4b757dedc333b9a9854b457b47.html
        """
        if self._wechat is None:
            return False
        return self._wechat.type is const.WECHAT_TYPE_SERVICE

    def _verify_code(self, code):
        """检查 code 是不是之前使用过的"""

        old = self.get_cookie(const.COOKIE_CODE)
        self.logger.debug("[_verify_code]old code: {}".format(old))
        self.logger.debug("[_verify_code]new code: {}".format(code))

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
        raise gen.Return(wechat)

    @gen.coroutine
    def _get_qx_wechat(self):
        wechat = yield self._get_current_wechat(qx=True)
        raise gen.Return(wechat)

    @gen.coroutine
    def _get_user_info(self, code):
        self._oauth_service.wechat = self._qx_wechat
        try:
            userinfo = yield self._oauth_service.get_userinfo_by_code(code)
            raise gen.Return(userinfo)
        except WeChatOauthError as e:
            self.logger.error("_get_user_info cookie code : {}".format(self.get_cookie(const.COOKIE_CODE)))
            self.logger.error("_get_user_info: {}".format(self.request))
            self.logger.error(e)

    @gen.coroutine
    def _get_user_openid(self, code):
        self._oauth_service.wechat = self._wechat
        try:
            openid, _ = yield self._oauth_service.get_openid_unionid_by_code(
                code)
            raise gen.Return(openid)
        except WeChatOauthError as e:
            self.logger.error("_get_user_openid: {}".format(self.request))
            self.logger.error(e)

    @gen.coroutine
    def _fetch_session(self):
        """尝试获取 session 并创建 current_user，如果获取失败走 oauth 流程"""
        ok = False
        session_id = to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        self.logger.debug("_fetch_session session_id: %s" % session_id)

        if session_id:
            if self.is_platform:
                self.logger.debug(
                    "is_platform _fetch_session session_id: {}".format(session_id))
                # 判断是否可以通过 session，直接获得用户信息，这样就不用跳授权页面
                ok = yield self._get_session_by_wechat_id(session_id, self._wechat.id)
                if not ok:
                    ok = yield self._get_session_by_wechat_id(session_id, self.settings['qx_wechat_id'])
            elif self.is_qx:
                ok = yield self._get_session_by_wechat_id(session_id, self.settings['qx_wechat_id'])

            elif self.is_help:
                # TODO 需讨论
                pass

            need_oauth = not ok

        else:
            need_oauth = True

        self.logger.debug("need_oauth: %s" % need_oauth)
        self.logger.debug("_unionid: %s" % self._unionid)
        self.logger.debug("_wxuser: %s" % self._wxuser)
        self.logger.debug("_qx_wechat: %s" % self._qx_wechat)

        if need_oauth:
            if self.in_wechat and not self._unionid:
                # unionid 不存在，则进行仟寻授权
                self.logger.debug("start oauth!!!!")
                self._oauth_service.wechat = self._qx_wechat
                url = self._oauth_service.get_oauth_code_userinfo_url()
                self.redirect(url)
                return
            else:
                self.logger.debug("beyond wechat start!!!")
                yield self._build_session()
                self.logger.debug("_build_session: %s" % self.current_user)
        else:
            self.logger.error("!!!!!!!need_oauth error!!!!!!!")
            self.logger.error("!!!!!!!need_oauth error current_user: {}".format(self.current_user))

    @gen.coroutine
    def _build_session(self):
        """用户确认向仟寻授权后的处理，构建 session"""

        self.logger.debug("start build_session")

        session = ObjectDict()
        session.wechat = self._wechat

        # qx session 中，只需要存储 id，unioid 即可，且俩变量一旦生成不会改变，不会影响 session 一致性
        # 该 session 只做首次仟寻登录查找各关联帐号所用(微信环境内)
        if self._unionid:
            # 只对微信 oauth 用户创建qx session
            session.qxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                unionid=self._unionid,
                wechat_id=self.settings['qx_wechat_id'],
                fields=['id', 'unionid']
            )
            session_id = self._make_new_session_id(session.qxuser.sysuser_id)
            self._save_qx_sessions(session_id, session.qxuser)
            self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True)

        # 登录，或非登录用户（非微信环境），都需要创建 mviewer_id
        mviewer_id = self._make_new_moseeker_viewer_id()
        self.set_secure_cookie(const.COOKIE_MVIEWERID, mviewer_id, httponly=True)

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
            "_get_session_by_wechat_id redis wechat_id:{} session: {}, key: {}".format(wechat_id, value, key))
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
    def build_session_by_user_id(self, user_id):
        """从 user_id 构建 session"""

        session = ObjectDict()
        self.logger.debug("build_session_by_user_id")

        # 非微信环境, 忽略 wxuser, qxuser
        session.wxuser = ObjectDict()
        session.qxuser = ObjectDict()

        session_id = self._make_new_session_id(user_id)
        self._save_ent_sessions(session_id, session)
        self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True)

    @gen.coroutine
    def _build_session_by_unionid(self, unionid):
        """从 unionid 构建 session"""

        session = ObjectDict()
        session_id = to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        self.logger.debug("_build_session_by_unionid")
        self.logger.debug("_build_session_by_unionid unionid: {}".format(unionid))
        self.logger.debug("_build_session_by_unionid session_id: {}".format(session_id))

        if not unionid:
            # 非微信环境, 忽略 wxuser, qxuser
            session.wxuser = ObjectDict()
            session.qxuser = ObjectDict()
        else:
            if self._wxuser:
                session.wxuser = self._wxuser
            else:
                session.wxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                    unionid=unionid, wechat_id=self._wechat.id)

            if self._qxuser:
                session.qxuser = self._qxuser
            else:
                session.qxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
                    unionid=unionid, wechat_id=self.settings['qx_wechat_id'])

            if session_id:
                # session_id = self._make_new_session_id(session.qxuser.sysuser_id)
                self._save_ent_sessions(session_id, session)

        yield self._add_sysuser_to_session(session, session_id)

        session.wechat = self._wechat
        self._add_jsapi_to_wechat(session.wechat)

        self.logger.debug("_build_session_by_unionid params: {}".format(self.params))
        if self.is_platform:
            yield self._add_company_info_to_session(session)
            self.logger.debug("_build_session_by_unionid company: {}".format(session.company))
        if self.params.recom:
            yield self._add_recom_to_session(session)
            self.logger.debug("_build_session_by_unionid recom: {}".format(session.recom))

        self.current_user = session

    def _save_qx_sessions(self, session_id, qxuser):
        """
        保存聚合号 session， 只包含 qxuser
        """

        key_qx = const.SESSION_USER.format(session_id, self.settings['qx_wechat_id'])
        self.redis.set(key_qx, ObjectDict(qxuser=qxuser), 60 * 60 * 24 * 30)
        self.logger.debug("refresh qx session redis key: {} session: {}".format(key_qx, ObjectDict(qxuser=qxuser)))

    def _save_ent_sessions(self, session_id, session):
        """
        保存企业号 session， 包含 wxuser, qxuser, sysuser
        """

        key_ent = const.SESSION_USER.format(session_id, self._wechat.id)
        self.redis.set(key_ent, session, 60 * 60 * 2)
        self.logger.debug("refresh ent session redis key: {} session: {}".format(key_ent, session))

    @gen.coroutine
    def _add_company_info_to_session(self, session):
        """拼装 session 中的 company, employee
        """

        session.company = yield self._get_current_company(session.wechat.company_id)
        employee = yield self.user_ps.get_valid_employee_by_user_id(
            user_id=session.sysuser.id, company_id=session.company.id)

        if employee:
            session.employee = employee

    @gen.coroutine
    def _get_current_company(self, company_id):
        """获得企业母公司信息"""

        conds = {'id': company_id}
        company = yield self.company_ps.get_company(conds=conds, need_conf=True)

        # 配色处理，如果theme_id为5表示公司使用默认配置，不需要将原始配色信息传给前端
        # 如果将theme_id为5的传给前端，会导致前端颜色无法正常显示默认颜色
        if company.conf_theme_id != 5:
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
        session.recom = yield self.user_ps.get_user_user({
            "id": recom_user_id
        })

    @gen.coroutine
    def _add_sysuser_to_session(self, session, session_id):
        """拼装 session 中的 sysuser"""

        user_id = self._get_user_id_from_session_id(session_id)
        session.sysuser = yield self.user_ps.get_user_user({
            "id": user_id
        })

    def _add_jsapi_to_wechat(self, wechat):
        """拼装 jsapi"""
        wechat.jsapi = JsApi(
            jsapi_ticket=wechat.jsapi_ticket,
            url=self.request.full_url())

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

    def _make_new_moseeker_viewer_id(self):
        """创建新的mviewer_id
        不论是登录，或非登录用户，都会有唯一的 mviewer_id，标识独立的用户。
        主要用于日志统计中 UV 的统计
        """

        while True:
            mviewer_id = const.SESSION_ID.format(
                "_",
                sha1(os.urandom(24)).hexdigest())
            return mviewer_id

    def _get_user_id_from_session_id(self, session_id):
        """从 session_id 中得到 user_id"""

        if session_id:
            session_id_list = re.match(r"([0-9]*)_([0-9a-z]*)_([0-9]*)", session_id)
            return session_id_list.group(1) if session_id_list.group(1) else ""
        else:
            return ""

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        # TODO 添加前端 url 的白名单参数
        add_namespace = ObjectDict(
            env=self.env,
            params=self.params,
            make_url=make_url,
            const=const,
            path=path,
            static_url=self.static_url,
            current_user=self.current_user,
            settings=self.settings)
        namespace.update(add_namespace)
        return namespace
