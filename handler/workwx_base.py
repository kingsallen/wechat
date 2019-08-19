# coding=utf-8

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
from oauth.wechat import WeChatOauth2Service, WeChatOauthError, JsApi, WorkWXOauth2Service
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
        self._workwx = None
        self._work_oauth_service = None
        self._sysuser = None
        self._workwx_userid = None
        self._workwx_user = None
        self._wxuser = None

    # PUBLIC API
    @check_signature
    @gen.coroutine
    def prepare(self):
        """用于生成 current_user"""
        self._wechat = yield self._get_current_wechat()
        company = yield self._get_current_company(self._wechat.company_id)
        self._workwx = yield self.workwx_ps.get_workwx(company.id, company.hraccount_id)
        self._work_oauth_service = WorkWXOauth2Service(
            self._workwx, self.fullurl())

        # 如果有 code，说明刚刚从企业微信 oauth 回来
        code = self.params.get("code")
        state = self.params.get("state")

        # 用户同意授权
        if code and self._verify_code(code):
            # 保存 code 进 cookie
            self.set_cookie(
                const.COOKIE_CODE,
                to_str(code),
                expires_days=1,
                httponly=True)

            if self.in_workwx:
                self.logger.debug("来自 workwx 的授权, 获得 code: {}".format(code))
                workwx_userinfo = yield self._get_user_info_workwx(code)
                if workwx_userinfo:
                    self.logger.debug("来自 workwx 的授权, 获得 workwx_userinfo:{}".format(workwx_userinfo))
                    self._sysuser = yield self._handle_user_info_workwx(workwx_userinfo)
                    # if self._WORKWX_REDIRECT:
                    #     return
                else:
                    self.logger.debug("来自 workwx 的 code 无效")
            else:
                pass
        else:
            pass

        # 构造并拼装 session
        yield self._fetch_session()

        # 内存优化
        self._wechat = None
        self._workwx = None
        self._work_oauth_service = None
        self._sysuser = None
        self._workwx_userid = None
        self._workwx_user = None
        self._wxuser = None

        self.logger.debug("workwx current_user:{}".format(self.current_user))
        self.logger.debug("+++++++++++++++WORKWX PREPARE OVER+++++++++++++++++++++")

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

        if need_oauth:
            if self.in_workwx and not self._workwx_userid:
                url = self._work_oauth_service.get_oauth_code_base_url()
                self.logger.debug("workwx_oauth_redirect_url: {}".format(url))
                self.redirect(url)
                return
            else:
                yield self._build_session()

    @gen.coroutine
    def _build_session(self):
        """用户确认向仟寻授权后的处理，构建 session"""

        self.logger.debug("workwx _build_session start")

        session = ObjectDict()
        session.wechat = self._wechat

        # # 该 session 只做首次仟寻登录查找各关联帐号所用(微信环境内)
        # if self._sysuser:
        #     # 只对微信 oauth 用户创建qx session
        #     session.workwx_user = yield self.workwx_ps.get_workwx_user(self._wechat.company_id, self._workwx_userid)
        #     self._session_id = self._make_new_session_id(
        #         self._sysuser.id)
        #     self.logger.info("workwx session_id:{}-----sysuser_id:{}".format(self._session_id, self._sysuser.id))
        #     self._pass_session.save_qx_sessions(
        #         self._session_id, session.workwx_user)
        #     self.set_secure_cookie(
        #         const.COOKIE_SESSIONID,
        #         self._session_id,
        #         httponly=True,
        #         domain=settings['root_host']
        #     )

        # 重置 wxuser，qxuser，构建完整的 session
        self._workwx_user = ObjectDict()
        self._wxuser = ObjectDict()
        if self._sysuser:
            yield self._build_session_by_unionid(self._sysuser)

    @gen.coroutine
    def _get_session_by_wechat_id(self, session_id, wechat_id):
        """尝试获取 session"""

        key = const.SESSION_USER.format(session_id, wechat_id)
        value = self.redis.get(key)
        self.logger.debug(
            "workwx _get_session_by_wechat_id redis wechat_id:{} session: {}, key: {}".format(
                wechat_id, value, key))
        if value:
            # 如果有 value， 返回该 value 作为 self.current_user
            session = ObjectDict(value)
            self._sysuser = yield self._add_sysuser_to_session(self._session_id)
            self._workwx_user = session.workwx_user
            self._workwx_userid = session.workwx_user.work_wechat_userid
            self._wxuser = session.wxuser
            yield self._build_session_by_unionid(self._unionid)
            raise gen.Return(True)

        raise gen.Return(False)

    @gen.coroutine
    def _build_session_by_unionid(self, sysuser):
        """从 unionid 构建 session"""

        session = ObjectDict()
        # session_id = to_str(self.get_secure_cookie(const.COOKIE_SESSIONID))
        if not sysuser:
            # 非微信环境, 忽略 wxuser, qxuser
            session.workwx_user = ObjectDict()
            session.wxuser = ObjectDict()
        else:
            session.workwx_user = yield self.workwx_ps.get_workwx_user(
                self._wechat.company_id, self._workwx_userid)
            session.wxuser = yield self.user_ps.self.get_wxuser_sysuser_id_wechat_id(
                sysuser_id=sysuser.id, wechat_id=self._wechat.id)

        if not self._session_id:
            self._session_id = self._make_new_session_id(
                sysuser.id)
            self.set_secure_cookie(
                const.COOKIE_SESSIONID,
                self._session_id,
                httponly=True,
                domain=settings['root_host'])

        if self.is_platform:
            self._pass_session.save_ent_sessions(
                self._session_id, session, self._wechat.id)

        session.sysuser = yield self._add_sysuser_to_session(self._session_id)

        session.wechat = self._wechat
        # self._add_jsapi_to_wechat(session.wechat)

        yield self._add_company_info_to_session(session)
        # if self.is_platform and self.params.recom:
        #     yield self._add_recom_to_session(session)

        self.current_user = session

    @gen.coroutine
    def _add_sysuser_to_session(self, session_id):
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
        # if sysuser.unionid and not session.qxuser:
        #     session.qxuser = yield self.user_ps.get_wxuser_unionid_wechat_id(
        #         unionid=sysuser.unionid, wechat_id=self.settings['qx_wechat_id'])

        return sysuser

    @gen.coroutine
    def _handle_user_info_workwx(self, workwx_userinfo):
        """
        根据 userId 创建 user_workwx 如果存在则不创建， 返回 wxuser_id
        创建 员工user_employee，绑定刚刚创建的 user_id

        userinfo 结构：
        ObjectDict(
            "userid": "zhangsan",
            "name": "李四",
            "department": [1, 2],
            "order": [1, 2],
            "position": "后台工程师",
            "mobile": "15913215421",
            "gender": "1",
            "email": "zhangsan@gzdev.com",
            "is_leader_in_dept": [1, 0],
            "avatar": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/0",
            "telephone": "020-123456",
            "enable": 1,
            "alias": "jackzhang",
            "address": "广州市海珠区新港中路",
        )
        """
        # 通过userid查询 这个企业微信成员 是不是已经存在
        self._workwx_userid = workwx_userinfo.userid
        workwx_user_record = yield self.workwx_ps.get_workwx_user(self.current_user.wechat.company_id, workwx_userinfo.userid)
        workwx_sysuser_id = 0
        # 企业微信成员 已经存在
        if workwx_user_record:
            workwx_sysuser_id = 0 if workwx_user_record.sys_user_id == '' else int(workwx_user_record.sys_user_id)
            if workwx_sysuser_id > 0:
                sysuser = yield self.user_ps.get_user_user({
                    "id": workwx_user_record.sys_user_id
                })
            else:
                sysuser = yield self._get_sysuser_by_mobile(workwx_userinfo)
        else:
            is_create_success = yield self.workwx_ps.create_workwx_user(
                workwx_userinfo,
                company_id=self.current_user.wechat.company_id,
                workwx_userid=workwx_userinfo.userid)

            sysuser = yield self._get_sysuser_by_mobile(workwx_userinfo)
        res_sysuser = yield self._is_valid_employee(sysuser, workwx_sysuser_id, workwx_userinfo.userid)
        return res_sysuser

    # 用mobile匹配user_user的username，如果存在，绑定仟寻用户和企业微信
    @gen.coroutine
    def _get_sysuser_by_mobile(self, workwx_userinfo):
        if workwx_userinfo.mobile:
            sysuser = yield self.user_ps.get_user_user({
                "username": workwx_userinfo.mobile
            })
        else:
            sysuser = None
        return sysuser

    #绑定企业微信用户和仟寻用户、保存session 这两个操作 必须在不跳转微信(直接跳转position页面)的情况下执行；在跳转微信的情况下很可能微信
    @gen.coroutine
    def _is_valid_employee(self, sysuser, workwx_sysuser_id, workwx_userid):
        #5s跳转页面
        if sysuser:
            # 判断是否是有效员工
            is_valid_employee = yield self.employee_ps.is_valid_employee(
                sysuser.id,
                self.current_user.wechat.company_id
            )
            # 如果是有效员工，不需要从企业微信跳转到微信,直接访问企业微信主页
            if is_valid_employee:
                yield self._bind_and_set_workwx_cookie(sysuser, workwx_sysuser_id, workwx_userid)
                return sysuser
            # 如果不是有效员工，先去判断是否关注了公众号
            is_subscribe = yield self.position_ps.get_hr_wx_user(sysuser.unionid, self.current_user.wechat.id)
            if is_subscribe:
                # 如果已经关注公众号，无需跳转微信，可生成员工信息之后访问主页
                yield self.workwx_ps.employee_bind(sysuser.id, self.current_user.wechat.company_id)
                yield self._bind_and_set_workwx_cookie(sysuser, workwx_sysuser_id, workwx_userid)
                return sysuser
            # 如果没有关注公众号，跳转微信
            # if workwx_sysuser_id > 0:  #如果在访问企业微信之前已经做过绑定(以前访问绑定过)，需要保存session，跳转微信之后无需再做绑定
            #     yield self._set_workwx_cookie(sysuser.id)
            # 其他认证方式或者已经关闭oms开关，不是有效员工直接跳转到企业微信二维码页面
            return sysuser
        else:
            return None

    # @gen.coroutine
    # def _set_workwx_cookie(self, sysuser_id):
    #     session_id = self.make_new_session_id(sysuser_id)
    #     self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True, domain=settings['root_host'])

    @gen.coroutine
    def _bind_and_set_workwx_cookie(self, sysuser, workwx_sysuser_id, workwx_userid):

        if workwx_sysuser_id <= 0:
            # 绑定仟寻用户和企业微信: 如果需要跳转微信，不能企业微信做绑定，必须去微信做绑定(因为有可能通过mobile绑定的仟寻用户跟跳转的仟寻用户不是同一个人)；如果不跳微信需要在企业微信做绑定
            yield self.workwx_ps.bind_workwx_qxuser(sysuser.id, workwx_userid, self.current_user.wechat.company_id)
        # yield self._set_workwx_cookie(sysuser.id)


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

    def _add_jsapi_to_wechat(self, wechat):
        """拼装 jsapi"""
        wechat.jsapi = JsApi(
            jsapi_ticket=wechat.jsapi_ticket,
            url=self.fullurl(encode=False))

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

        # if not self.domain in self.request.full_url():
        #     full_url = full_url.replace(self.settings.m_domain, self.domain)

        if not encode:
            return full_url
        return url_subtract_query(full_url, ['code', 'state'])

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
        client_env = ObjectDict({"name": self._client_env})
        namespace.update({"client_env": client_env}) #前端用
        return namespace

    def _verify_code(self, code):
        """检查 code 是不是之前使用过的"""

        old = self.get_cookie(const.COOKIE_CODE)

        if not old:
            return True
        return str(old) != str(code)
