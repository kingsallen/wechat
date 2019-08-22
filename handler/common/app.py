# coding=utf-8

import re
from handler.base import BaseHandler
from handler.metabase import MetaBaseHandler

from tornado import gen
from util.common.decorator import handle_response, authenticated
from util.common import ObjectDict
import conf.common as const
import conf.path as path
from oauth.wechat import JsApi


class WxWorkDomainVerifyHandler(MetaBaseHandler):

    @gen.coroutine
    def get(self, verify_content):
        self.set_header('Content-Type', 'text/plain')
        self.set_status(200)
        self.write(verify_content)
        return


class IndexHandler(BaseHandler):
    """页面Index, 单页应用使用"""

    # 需要静默授权的 path
    _NEED_AUTH_PATHS = ['usercenter', 'employee', 'asist']

    @handle_response
    @gen.coroutine
    def get(self):

        method_list = re.search("/app/([a-zA-Z][a-zA-Z0-9-_]*)", self.request.uri)
        method = method_list.group(1) if method_list else "default"

        self._save_dqpid_cookie()

        self.logger.debug("common IndexHandler")

        try:
            if re.search('/app/employee/recommends', self.request.uri):
                yield getattr(self, 'get_expired')()
            elif method in self._NEED_AUTH_PATHS:
                yield getattr(self, 'get_auth_first')()
            else:
                yield getattr(self, 'get_default')()

            # 重置 event，准确描述
            self._event = self._event + method

        except Exception as e:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def get_default(self):
        self.render(template_name="system/app.html")

    @handle_response
    @authenticated
    @gen.coroutine
    def get_expired(self):
        self.render_page(
            template_name="adjunct/msg-expired.html",
            data={
                'button': {
                    'text': self.locale.translate(const.REFERRAL_EXPIRED_MESSAGE),
                    'link': self.make_url(
                        path.REFERRAL_PROGRESS,
                        self.params)
                }
            })

    @handle_response
    @authenticated
    @gen.coroutine
    def get_auth_first(self):
        """个人中心，需要使用authenticated判断是否登录，及静默授权"""
        self.render(template_name="system/app.html")

    def _save_dqpid_cookie(self):
        """ 新用户在申请职位的时候进入老六步创建简历时
        在 /app/profile/new 页面，保存 pid 进 session cookie <dqpid>

        Profile 创建成功后在根据 dqpid 是否存在判断跳转
        """
        if re.match(r"/app/profile/new", self.request.uri):
            if self.params.pid:
                self.set_cookie('dqpid', self.params.pid)


class ConfigHandler(BaseHandler):
    """微信 config 配置"""

    @handle_response
    @gen.coroutine
    def get(self):

        target_url = self.params.target

        jsapi = JsApi(
            jsapi_ticket=self.current_user.wechat.jsapi_ticket,
            url=target_url)

        config = ObjectDict({
            "debug": False,
            "appId": self.current_user.wechat.appid,
            "timestamp": jsapi.timestamp,
            "nonceStr": jsapi.nonceStr,
            "signature": jsapi.signature,
            "jsApiList": ["onMenuShareTimeline",
                          "onMenuShareAppMessage",
                          "updateTimelineShareData",
                          "updateAppMessageShareData",
                          "onMenuShareQQ",
                          "updateTimelineShareData",
                          "updateAppMessageShareData",
                          "onMenuShareWeibo",
                          "hideOptionMenu",
                          "showOptionMenu",
                          "startRecord",
                          "stopRecord",
                          "onVoiceRecordEnd",
                          "playVoice",
                          "pauseVoice",
                          "stopVoice",
                          "onVoicePlayEnd",
                          "uploadVoice",
                          "translateVoice",
                          "downloadVoice",
                          "hideMenuItems",
                          "showMenuItems",
                          "hideAllNonBaseMenuItem",
                          "showAllNonBaseMenuItem"]
        })
        self.send_json_success(data=config)
