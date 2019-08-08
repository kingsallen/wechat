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
from oauth.wechat import WeChatOauthError, JsApi, WorkWXOauth2Service
from util.common.decorator import check_signature


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
        super(BaseHandler, self).__init__(application, request, **kwargs)

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
            self._workwx, self.request.full_url())

        code = self.params.get("code")
        if code:
            self.logger.debug("来自 workwx 的授权, 获得 userinfo")
            workwx_userinfo = yield self._get_user_info_workwx(code)
            if workwx_userinfo:
                self.logger.debug("来自 workwx 的授权, 获得 userinfo:{}".format(workwx_userinfo))
                yield self._handle_user_info_workwx(workwx_userinfo)
            else:
                self.logger.debug("来自 workwx 的 code 无效")
            yield self._build_workwx_session(workwx_userinfo)


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
        #企业微信主页:职位列表页
        workwx_page = self.make_url(path.POSITION_LIST, self.params, host=self.host)
        # 通过userid查询 这个企业微信成员 是不是已经存在
        workwx_user_record = yield self.workwx_ds.get_workwx_user(self._wechat.company_id, workwx_userinfo.userid)
        # 企业微信成员 已经存在
        if workwx_user_record:
            if workwx_user_record.sysuser_id >= 0:
                sysuser = yield self.user_ps.get_user_user({
                    "id": workwx_user_record.sysuser_id
                })
            elif workwx_userinfo.mobile:  #用mobile匹配user_user的username，如果存在，绑定仟寻用户和企业微信
                sysuser = yield self.user_ps.get_user_user({
                    "username": workwx_userinfo.mobile
                })
                if sysuser: #绑定仟寻用户和企业微信
                    bind_res = yield self.workwx_ds.bind_workwx_qxuser(sysuser.id, workwx_userinfo.userid, workwx_userinfo.company_id)
            else:
                sysuser = None

            if sysuser:
                is_valid_employee = yield self.employee_ps.is_valid_employee(
                    workwx_user_record.sysuser_id,
                    workwx_user_record.company_id
                )
                if is_valid_employee: #如果是有效员工，不需要从企业微信跳转到微信,直接访问企业微信主页
                    self.redirect(workwx_page)
                    return
                  #如果不是有效员工，先去判断是否关注了公众号
                is_subscribe = yield self.position_ds.get_hr_wx_user(sysuser.unionid, self._wechat.id)
                if is_subscribe：

                    self.redirect(workwx_page)
                    return
            else:

        is_create_success = yield self.workwx_ps.create_workwx_user(
            workwx_userinfo,
            company_id=self._wechat.company_id,
            workwx_userid=workwx_userinfo.userid)

        if is_create_success:
            self._log_customs.update(new_user=const.YES)

        self.logger.debug("[_handle_workwx_user_info]workwx_user_id: {}".format(workwx_user_id))

        workwx_user = yield self.workwx_ps.get_workwx_user({
            "company_id": self._wechat.company_id,
            "workwx_userid": workwx_userinfo.userid  # 保证查找正常的 user record
        })


    @gen.coroutine
    def _build_workwx_session(self, workwx_userinfo):
        wechat = yield self.wechat_ps.get_wechat(conds={
            "company_id":
        })
        session_id = self.make_new_session_id(workwx_userinfo.userid + '_' + workwx_userinfo.company_id)
        self.set_secure_cookie(const.COOKIE_SESSIONID, session_id, httponly=True, domain=settings['root_host'])
        self.params.update(wechat_signature=wechat.signature)
        next_url = self.make_url(path.POSITION_LIST,
                                 self.params,
                                 host=self.host)
        self.send_json_success(data={
            "next_url": next_url
        })
