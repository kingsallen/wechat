# coding=utf-8

import uuid
import ast

from tornado import gen

import conf.common as const
import conf.path as path

from setting import settings
from handler.base import BaseHandler
from handler.metabase import MetaBaseHandler
from util.common.decorator import handle_response, check_env, authenticated
from util.tool.dict_tool import ObjectDict
from util.tool.str_tool import to_str
from oauth.wechat import WeChatOauthError, JsApi, WorkWXOauth2Service, WeChatOauth2Service
from util.common.decorator import check_signature
from util.tool.url_tool import url_subtract_query, make_url


class JoywokOauthHandler(MetaBaseHandler):

    @handle_response
    @check_env(3)
    @gen.coroutine
    def get(self):
        """更新joywok的授权信息，及获取joywok用户信息"""
        # 获取登录状态，已登录跳转到职位列表页
        is_oauth = yield self._get_session()
        if is_oauth:
            wechat = yield self.wechat_ps.get_wechat(conds={"company_id": const.MAIDANGLAO_COMPANY_ID})
            self.params.update(wechat_signature=wechat.signature)
            next_url = self.make_url(path.POSITION_LIST, self.params, host=self.host)
            self.redirect(next_url)
            return
        headers = ObjectDict({"Referer": self.request.full_url()})
        res = yield self.joywok_ps.get_joywok_info(appid=settings['joywok_appid'], method=const.JMIS_SIGNATURE, headers=headers)
        client_env = ObjectDict({
            "name": self._client_env,
            "args": ObjectDict({
                "appid": res.app_id,
                "signature": res.signature,
                "timestamp": res.timestamp,
                "nonceStr": res.nonce,
                "corpid": res.corp_id,
                "redirect_url": res.redirect_url
            })
        })
        self.namespace = {"client_env": client_env,
                          "params": self.params}
        self.render_page("joywok/entry.html", data=ObjectDict())

    @gen.coroutine
    def _get_session(self):
        # 获取session
        self._session_id = to_str(
            self.get_secure_cookie(
                const.COOKIE_SESSIONID))

        is_oauth = yield self._get_session_by_wechat_id(self._session_id)
        return is_oauth

    @gen.coroutine
    def _get_session_by_wechat_id(self, session_id, wechat_id=const.MAIDANGLAO_WECHAT_ID):
        """尝试获取 session"""

        key = const.SESSION_USER.format(session_id, wechat_id)
        value = self.redis.get(key)
        self.logger.debug(
            "_get_joywok_session_by_wechat_id redis wechat_id:{} session: {}, key: {}".format(
                wechat_id, value, key))
        if value:
            raise gen.Return(True)

        raise gen.Return(False)


class JoywokInfoHandler(MetaBaseHandler):

    @handle_response
    @check_env(3)
    @gen.coroutine
    def post(self):
        """通过免登陆码获取用户信息"""
        code = self.json_args.code
        joywok_user_info = yield self.joywok_ps.get_joywok_info(code=code, method=const.JMIS_USER_INFO)

        ret = yield self.user_ps.get_user_by_joywok_info(joywok_user_info, company_id=const.MAIDANGLAO_COMPANY_ID)
        wechat = yield self.wechat_ps.get_wechat(conds={
            "company_id": const.MAIDANGLAO_COMPANY_ID
        })
        if ret.data:
            session_id = self.make_new_session_id(ret.data.sysuser_id)
            self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True, domain=settings['root_host'])
            self.params.update(wechat_signature=wechat.signature)
            next_url = self.make_url(path.POSITION_LIST,
                                     self.params,
                                     host=self.host)
            self.send_json_success(data={
                "next_url": next_url
            })
        else:
            identify_code = str(uuid.uuid4())
            self.redis.set(const.JOYWOK_IDENTIFY_CODE.format(identify_code), joywok_user_info, ttl=60*60*24*7)
            url = self.make_url(path.JOYWOK_AUTO_AUTH, host=self.host, str_code=identify_code, wechat_signature=wechat.signature)
            self.send_json_success(data={
                "share": ObjectDict({
                    "title": const.PAGE_JOYWOK_AUTO_BIND,
                    "url": url,
                })
            })


class JoywokAutoAuthHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """joywok转发到微信端的关注提示页"""
        self.render_page(template_name="joywok/forward-weixin.html", data=ObjectDict())




class WorkWXOauthHandler(MetaBaseHandler):

    def __init__(self, application, request, **kwargs):
        super(WorkWXOauthHandler, self).__init__(application, request, **kwargs)

        # 构建 session 过程中会缓存一份当前企业微信信息
        self._workwx = None
        self._wechat = None
        # 处理 oauth 的 service, 会在使用时初始化
        self._work_oauth_service = None

    @handle_response
    @check_env(4)
    @check_signature
    @gen.coroutine
    def get(self):
        """更新joywok的授权信息，及获取joywok用户信息"""
        # 获取登录状态，已登录跳转到职位列表页
        # 初始化 企业微信 oauth service
        self._wechat = yield self._get_current_wechat()
        company = yield self.company_ps.get_company(conds={'id': self._wechat.company_id}, need_conf=True)
        self._workwx = yield self.workwx_ps.get_workwx(company.id, company.hraccount_id)
        self._work_oauth_service = WorkWXOauth2Service(
            self._workwx, self.fullurl())

        code = self.params.get("code")
        if code:
            self.logger.debug("来自 workwx 的授权, 获得 workwx_userinfo")
            workwx_userinfo = yield self._get_user_info_workwx(code)
            if workwx_userinfo:
                self.logger.debug("来自 workwx 的授权, 获得 workwx_userinfo:{}".format(workwx_userinfo))
                yield self._handle_user_info_workwx(workwx_userinfo)
            else:
                self.logger.debug("来自 workwx 的 code 无效")
            # yield self._build_workwx_session(workwx_userinfo)


        is_oauth = yield self._get_session()
        if is_oauth:
            # self.params.update(wechat_signature=wechat.signature)
            next_url = self.make_url(path.POSITION_LIST, self.params, host=self.host)
            self.redirect(next_url)
            return

        url = self._work_oauth_service.get_oauth_code_base_url()
        self.logger.debug("workwx_oauth_redirect_url: {}".format(url))
        self.redirect(url)

    @gen.coroutine
    def _build_workwx_session(self, workwx_userinfo):

        session_id = self.make_new_session_id(str(workwx_userinfo.userid) + '_' + str(workwx_userinfo.company_id))
        self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True, domain=settings['root_host'])
        self.redis.set(session_id, workwx_userinfo, ttl=60 * 60 * 24 * 7)

    @gen.coroutine
    def _get_session(self):
        # 获取session
        self._session_id = to_str(
            self.get_secure_cookie(
                const.COOKIE_SESSIONID))

        is_oauth = yield self._get_session_by_wechat_id(self._session_id)
        return is_oauth

    @gen.coroutine
    def _get_session_by_wechat_id(self, session_id, wechat_id=const.MAIDANGLAO_WECHAT_ID):
        """尝试获取 session"""

        key = const.SESSION_USER.format(session_id, wechat_id)
        value = self.redis.get(key)
        self.logger.debug(
            "_get_workwx_session_by_wechat_id redis wechat_id:{} session: {}, key: {}".format(
                wechat_id, value, key))
        if value:
            raise gen.Return(True)

        raise gen.Return(False)

    @gen.coroutine
    def _get_current_wechat(self):

        signature = self.params['wechat_signature']
        wechat = yield self.wechat_ps.get_wechat(conds={
            "signature": signature
        })
        if not wechat:
            self.write_error(http_code=404)
            return

        raise gen.Return(wechat)

    @gen.coroutine
    def _get_user_info_workwx(self, code):
        try:
            userinfo = yield self._work_oauth_service.get_userinfo_by_code(code)
            raise gen.Return(userinfo)
        except WeChatOauthError as e:
            raise gen.Return(None)

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
        #5s跳转页面
        workwx_fivesec_url = self.make_url(path.WOKWX_FIVESEC_PAGE, self.params) + "&workwx_userid={}&company_id={}".format(workwx_userinfo.userid,self._wechat.company_id)  # 如果没有关注公众号, 跳转微信
        # 通过userid查询 这个企业微信成员 是不是已经存在
        workwx_user_record = yield self.workwx_ps.get_workwx_user(self._wechat.company_id, workwx_userinfo.userid)
        # 企业微信成员 已经存在
        if workwx_user_record:
            workwx_sysuser_id = int(workwx_user_record.sysuser_id)
            if workwx_sysuser_id > 0:
                sysuser = yield self.user_ps.get_user_user({
                    "id": workwx_user_record.sysuser_id
                })
            elif workwx_userinfo.mobile:  #用mobile匹配user_user的username，如果存在，绑定仟寻用户和企业微信
                sysuser = yield self.user_ps.get_user_user({
                    "username": workwx_userinfo.mobile
                })
            else:
                sysuser = None

        else:
            workwx_sysuser_id = 0
            is_create_success = yield self.workwx_ps.create_workwx_user(
                workwx_userinfo,
                company_id=self._wechat.company_id,
                workwx_userid=workwx_userinfo.userid)

            if is_create_success:
                if workwx_userinfo.mobile:
                    sysuser = yield self.user_ps.get_user_user({
                        "username": workwx_userinfo.mobile
                    })

        if sysuser:
            session_id = self.make_new_session_id(sysuser.id)
            self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True, domain=settings['root_host'])
            yield self._is_valid_employee(sysuser, workwx_fivesec_url, workwx_sysuser_id, workwx_userinfo.userid)
        else:
            self.redirect(workwx_fivesec_url)
            return


    @gen.coroutine
    def _is_valid_employee(self, sysuser, workwx_fivesec_url, workwx_sysuser_id, workwx_userid):
        """员工认证"""
        # 企业微信主页:职位列表页
        workwx_home_url = self.make_url(path.POSITION_LIST, self.params, host=self.host)

        is_valid_employee = yield self.employee_ps.is_valid_employee(
            sysuser.id,
            self._wechat.company_id
        )
        if is_valid_employee:  # 如果是有效员工，不需要从企业微信跳转到微信,直接访问企业微信主页
            if workwx_sysuser_id <= 0:
                #绑定仟寻用户和企业微信: 如果需要跳转微信，不能企业微信做绑定，必须去微信做绑定(因为有可能通过mobile绑定的仟寻用户跟跳转的仟寻用户不是同一个人)；如果不跳微信需要在企业微信做绑定
                yield self.workwx_ps.bind_workwx_qxuser(sysuser.id, workwx_userid, self._wechat.company_id)
            self.redirect(workwx_home_url)
            return
        # 如果不是有效员工，先去判断是否关注了公众号
        is_subscribe = yield self.position_ps.get_hr_wx_user(sysuser.unionid, self._wechat.id)
        if is_subscribe:
            # 生成员工信息: 如果已经关注公众号，无需跳转微信，可生成员工信息之后访问主页
            yield self.workwx_ps.employee_bind(sysuser.id, self._wechat.company_id)
            if workwx_sysuser_id <= 0:
                #绑定仟寻用户和企业微信
                yield self.workwx_ps.bind_workwx_qxuser(sysuser.id, workwx_userid, self._wechat.company_id)
            self.redirect(workwx_home_url)
            return

        self.redirect(workwx_fivesec_url)
        return


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


class FiveSecSkipWXHandler(MetaBaseHandler):

    @handle_response
    @check_env(4)
    @check_signature
    @gen.coroutine
    def get(self):
        """企业微信5s跳转页"""
        component_access_token = BaseHandler.component_access_token
        wechat = yield self._get_current_wechat()
        redirect_url = self.make_url(path.WECHAT_QRCODE_PAGE, self.params)
        # 初始化 oauth service
        wx_oauth_service = WeChatOauth2Service(wechat, redirect_url, component_access_token)

        # if self.in_workwx:
        #     self._oauth_service.redirect_url += "&workwx_userid={}&company_id=".format(self._workwx_userid,
        #                                                                                self._wechat.company_id)
        wx_oauth_url = wx_oauth_service.get_oauth_code_userinfo_url()
        self.logger.debug("from_workwx_to_qx_oauth_url: {}".format(wx_oauth_url))
        self.render_page(template_name="adjunct/wxwork-bind-redirect.html", data=ObjectDict({"redirect_link": wx_oauth_url}))

    @gen.coroutine
    def _get_current_wechat(self):

        signature = self.params['wechat_signature']
        wechat = yield self.wechat_ps.get_wechat(conds={
            "signature": signature
        })
        if not wechat:
            self.write_error(http_code=404)
            return

        raise gen.Return(wechat)



class WechatQrcodeHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        workwx_userid = self.params.workwx_userid
        company_id = self.params.company_id

        #绑定企业微信成员和仟寻用户：只要跳转微信，就必须在微信做绑定，不在企业微信做绑定
        yield self.workwx_ps.bind_workwx_qxuser(self.current_user.sysuser.id, workwx_userid, company_id)

        #@@@@@@下面代码是否写在扫码事件里面
        # is_valid_employee = yield self.employee_ps.is_valid_employee(
        #     self.current_user.sysuser.id,
        #     company_id
        # )
        # if not is_valid_employee:  # 如果不是有效员工，需要需要生成员工信息
        #     yield self.workwx_ps.employee_bind(self.current_user.sysuser.id, company_id)  # 如果已经关注公众号，无需跳转微信，可生成员工信息之后访问主页
        self.render_page(template_name="adjunct/wxwork-qrcode.html", data=ObjectDict())
