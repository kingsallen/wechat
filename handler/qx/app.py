# coding=utf-8

from tornado import gen

from handler.base import BaseHandler
from oauth.wechat import JsApi
from util.common.decorator import handle_response, gamma_welcome
from util.common import ObjectDict


class IndexHandler(BaseHandler):
    """页面Index, Gamma单页应用使用"""

    @handle_response
    @gamma_welcome
    @gen.coroutine
    def get(self):
        self.logger.debug("qx IndexHandler")

        self.render(template_name="qx/qx.html")

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
                          "onMenuShareQQ",
                          "onMenuShareWeibo",
                          "hideOptionMenu",
                          "showOptionMenu",
                          "hideMenuItems",
                          "showMenuItems",
                          "hideAllNonBaseMenuItem",
                          "showAllNonBaseMenuItem"]
        })
        self.send_json_success(data=config)


class NotFoundHandler(BaseHandler):

    @handle_response
    def get(self):
        self.send_json_error(message="not found", http_code=404)

    @handle_response
    def post(self):
        self.send_json_error(message="not found", http_code=404)
