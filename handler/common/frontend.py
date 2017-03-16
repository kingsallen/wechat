# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import UIModule

from handler.base import BaseHandler
from util.common.decorator import handle_response

class NavMenuModule(UIModule):
    """老微信样式的 menu"""

    def render(self):
        return self.render_string('refer/neo_common/neo_navmenu.html')


class JSSDKErrorHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def post(self):
        """记录微信 js 调用错误信息"""

        self.log_info({
            "jserror": self.json_args['jssdk_error']
        })
        self.logger.error("[JSSDKErrorHandler]wx_js_sdkerror:{}".format(self.json_args['jssdk_error']))

        self.send_json_success()
