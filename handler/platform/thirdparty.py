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

        client_env = ObjectDict({"name": self._client_env})
        self.namespace = {"client_env": client_env}
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
        #如果已经绑定过(以前访问绑定过),无需再绑定
        if int(workwx_user_record.sys_user_id) > 0:
           # 如果workwx_user_record.sys_user_id跟self.current_user.sysuser.id不一致，说明当前用户不是绑定用户，需要弹出提示
           pass
        else:
            yield self.workwx_ps.bind_workwx_qxuser(self.current_user.sysuser.id, workwx_userid, company_id)
        #如果已经关注公众号，说明已经做完员工认证，生成员工信息，跳转3s跳转页，再跳转到职位列表
        if self.current_user.wxuser.is_subscribe:
            is_valid_employee = yield self.employee_ps.is_valid_employee(
                self.current_user.sysuser.id,
                company_id
            )
            if not is_valid_employee:  # 如果不是有效员工，需要需要生成员工信息
                yield self.workwx_ps.employee_bind(self.current_user.sysuser.id, company_id)

            three_sec_wechat_url =  self.make_url(path.WECHAT_THREESEC_PAGE, self.params)
            self.redirect(three_sec_wechat_url)
            return
        self.render_page(template_name="adjunct/wxwork-qrcode.html", data=ObjectDict())


class WorkwxQrcodeHandler(MetaBaseHandler):

    @handle_response
    @check_env(4)
    @check_signature
    @gen.coroutine
    def get(self):
        # session = ObjectDict()
        self._wechat = yield self._get_current_wechat()
        # session.wechat = self._wechat
        # company = yield self.company_ps.get_company(conds={'id': self._wechat.company_id}, need_conf=True)
        # session.company = company
        # self.current_user = session

        client_env = ObjectDict({"name": self._client_env})
        self.namespace = {"client_env": client_env}
        data = yield self._get_wechat_info(self._wechat)
        self.render_page(template_name="adjunct/wxwork-qrcode-simple.html", data=data)

    @gen.coroutine
    def _get_wechat_info(self, wechat):
        pattern_id = self.params.scene or 99
        str_scene = self.params.str_scene or ''  # 字符串类型的场景值
        str_code = self.params.str_code or ''  # 字符串类型的自定义参数
        scene_code = const.TEMPORARY_CODE_STR_SCENE.format(str_scene, str_code)
        if str_code and str_scene:
            wechat_info = yield self.wechat_ps.get_wechat_in_workwx(wechat, scene_id=scene_code, action_name="QR_STR_SCENE")
        else:
            if int(pattern_id) == const.QRCODE_POSITION and self.params.pid:
                scene_id = int('11111000000000000000000000000000', base=2) + int(self.params.pid)
            else:
                scene_id = int('11110000000000000000000000000000', base=2) + int(pattern_id)
            wechat_info = yield self.wechat_ps.get_wechat_in_workwx(self.current_user, scene_id=scene_id)
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


# class WorkwxSubInfoHandler(MetaBaseHandler):
#     """
#     获取微信信息
#     字符类型的自定义参数的格式为{场景值(大写)}_{自定义字符串}，场景值必须为大写英文字母
#     int类型 scene_id规范为：32位二进制, 5位type + 27位自定义编号(比如hrid, userid)。见 https://wiki.moseeker.com/weixin.md
#     """
#     @handle_response
#     @check_env(4)
#     @check_signature
#     @gen.coroutine
#     def get(self):
#         session = ObjectDict()
#         self._wechat = yield self._get_current_wechat()
#         session.wechat = self._wechat
#         self.current_user = session
#
#         pattern_id = self.params.scene or 99
#         str_scene = self.params.str_scene or ''  # 字符串类型的场景值
#         str_code = self.params.str_code or ''  # 字符串类型的自定义参数
#         scene_code = const.TEMPORARY_CODE_STR_SCENE.format(str_scene, str_code)
#         if str_code and str_scene:
#             wechat = yield self.wechat_ps.get_workwx_info(self.current_user, scene_id=scene_code, action_name="QR_STR_SCENE")
#         else:
#             if int(pattern_id) == const.QRCODE_POSITION and self.params.pid:
#                 scene_id = int('11111000000000000000000000000000', base=2) + int(self.params.pid)
#             else:
#                 scene_id = int('11110000000000000000000000000000', base=2) + int(pattern_id)
#             wechat = yield self.wechat_ps.get_workwx_info(self.current_user, scene_id=scene_id)
#         self.send_json_success(data=wechat)
#         return
#
#     @gen.coroutine
#     def _get_current_wechat(self, qx=False):
#         if qx:
#             signature = self.settings['qx_signature']
#         else:
#             signature = self.params['wechat_signature']
#         wechat = yield self.wechat_ps.get_wechat(conds={
#             "signature": signature
#         })
#         if not wechat:
#             self.write_error(http_code=404)
#             return
#
#         raise gen.Return(wechat)


class EmployeeThreesecSkipHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """微信3s跳转职位列表页"""

        position_list_url = self.make_url(path.EMPLOYEE_PORTAL, self.params)
        self.render_page(template_name="adjunct/wxwork-verified-redirect.html", data=ObjectDict({"redirect_link": position_list_url}))
