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
from util.tool.url_tool import url_subtract_query
from util.tool.str_tool import to_str, match_session_id
from util.common.exception import MyException, InfraOperationError


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


class FiveSecSkipWXHandler(MetaBaseHandler):

    @handle_response
    @check_env(4)
    @check_signature
    @gen.coroutine
    def get(self):
        """企业微信5s跳转页"""
        component_access_token = BaseHandler.component_access_token
        qx_wechat = yield self._get_current_wechat(qx=True)

        wechat_qrcode_url = self.make_url(path.WECHAT_QRCODE_PAGE, self.params)
        # 初始化 oauth service
        wx_oauth_service = WeChatOauth2Service(qx_wechat, wechat_qrcode_url, component_access_token)
        wx_oauth_url = wx_oauth_service.get_oauth_code_userinfo_url()

        self.logger.debug("from_workwx_to_qx_oauth_url: {}".format(wx_oauth_url))
        self.render_page(template_name="adjunct/wxwork-bind-redirect.html", data=ObjectDict({"redirect_link": wx_oauth_url}))

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


class EmployeeQrcodeHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        workwx_userid = self.params.workwx_userid
        company_id = self.params.company_id
        workwx_user_record = yield self.workwx_ps.get_workwx_user(self.current_user.wechat.company_id, workwx_userid)
        sysuser_workwx_user = yield self.workwx_ps.get_workwx_user_by_sysuser_id(
            self.current_user.sysuser.id, company_id=self.current_user.wechat.company_id)

        if int(workwx_user_record.sys_user_id) > 0 and workwx_user_record.sys_user_id != self.current_user.sysuser.id:
            # raise MyException("该企业微信号已绑定其他仟寻账号！")
            self.render_page(
                'system/info.html',
                data={
                    'code': 500,
                    'message': "该企业微信号已绑定其他仟寻账号！"
                },
                http_code=500
            )
            return
        elif int(workwx_user_record.sys_user_id) <= 0 and sysuser_workwx_user:
            # raise MyException("该微信号已绑定其他账号！")
            self.render_page(
                'system/info.html',
                data={
                    'code': 500,
                    'message': "该微信号已绑定其他账号！"
                },
                http_code=500
            )
            return

        #如果已经关注公众号，说明已经做完员工认证，生成员工信息，跳转3s跳转页，再跳转到职位列表
        if self.current_user.wxuser.is_subscribe:
            # 如果已经绑定过(以前访问绑定过),无需再绑定
            if int(workwx_user_record.sys_user_id) <= 0:
                ret = yield self.workwx_ps.bind_workwx_qxuser(self.current_user.sysuser.id, workwx_userid, company_id)
                if ret.code != const.NEWINFRA_API_SUCCESS:
                    self.render_page(
                        'system/info.html',
                        data={
                            'code': 500,
                            'message': ret.message
                        },
                        http_code=500
                    )
                    return

            is_valid_employee = yield self.employee_ps.is_valid_employee(
                self.current_user.sysuser.id,
                company_id
            )
            if not is_valid_employee:  # 如果不是有效员工，需要需要生成员工信息
                try:
                    yield self.workwx_ps.employee_bind(self.current_user.sysuser.id, company_id)
                except Exception as e:
                    yield self.workwx_ps.unbind_workwx_qxuser(self.current_user.sysuser.id, workwx_userid, self._wechat.company_id)
                    raise InfraOperationError(e)

            three_sec_wechat_url =  self.make_url(path.WECHAT_THREESEC_PAGE, self.params)
            self.redirect(three_sec_wechat_url)
            return
        self.render_page(template_name="adjunct/wxwork-qrcode.html", data=ObjectDict({"str_code": workwx_userid}))


class WorkwxQrcodeHandler(MetaBaseHandler):

    @handle_response
    @check_env(4)
    @check_signature
    @gen.coroutine
    def get(self):
        self._wechat = yield self._get_current_wechat()

        data = yield self._get_wechat_info(self._wechat)
        self.render_page(template_name="adjunct/wxwork-qrcode-simple.html", data=ObjectDict({"wechat": data}))

    @gen.coroutine
    def _get_wechat_info(self, wechat):
        # str_scene = self.params.str_scene or ''  # 字符串类型的场景值
        str_scene = "WORKWX"  # 字符串类型的场景值
        str_code = self.params.str_code or ''  # 字符串类型的自定义参数
        scene_code = const.TEMPORARY_CODE_STR_SCENE.format(str_scene, str_code)
        wechat_info = yield self.wechat_ps.get_wechat_in_workwx(wechat, scene_id=scene_code, action_name="QR_STR_SCENE")
        return wechat_info

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


class EmployeeThreesecSkipHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """微信3s跳转职位列表页"""

        position_list_url = self.make_url(path.EMPLOYEE_PORTAL, self.params)
        self.render_page(template_name="adjunct/wxwork-verified-redirect.html", data=ObjectDict({"redirect_link": position_list_url}))
