# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response
from util.common import ObjectDict


class IndexHandler(BaseHandler):
    """页面Index, Gamma单页应用使用"""

    @handle_response
    @gen.coroutine
    def get(self):
        self.logger.debug("IndexHandler qx")
        self.logger.debug("index uri:{}".format(self.request))

        self.render(template_name="qx/qx.html")

class ConfigHandler(BaseHandler):
    """微信 config 配置"""

    @handle_response
    @gen.coroutine
    def get(self):

        config = ObjectDict({
            "debug": False,
            "appId": self.current_user.wechat.appid,
            "timestamp": self.current_user.wechat.jsapi.timestamp,
            "nonceStr": self.current_user.wechat.jsapi.nonceStr,
            "signature": self.current_user.wechat.jsapi.signature,
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
