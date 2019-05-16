# coding=utf-8


from tornado import gen


import conf.common as const

from handler.base import BaseHandler
from handler.metabase import MetaBaseHandler
from util.common.decorator import handle_response, check_env
from util.tool.dict_tool import ObjectDict


class JoywokOauthHandler(MetaBaseHandler):

    @handle_response
    @check_env(3)
    @gen.coroutine
    def get(self):
        """更新joywok的授权信息，及获取joywok用户信息"""
        res = self.joywok_ps.get_joywok_info(appid=const.ENV_ARGS.get(self._client_env), method=const.JMIS_SIGNATURE)
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
        self.namespace = {"client_env": client_env}
        self.render_page("joywok/entry.html", data=ObjectDict())


class JoywokInfoHandler(MetaBaseHandler):

    @handle_response
    @check_env(3)
    @gen.coroutine
    def post(self):
        """通过免登陆码获取用户信息"""
        code = self.json_args.code
        res = self.joywok_ps.get_joywok_info(code=code, method=const.JMIS_USER_INFO)
        self.user_ps.get_user_by_joywok_info()


