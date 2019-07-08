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
