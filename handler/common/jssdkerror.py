# coding=utf-8

# @Time    : 3/16/17 10:40
# @Author  : panda (panyuxin@moseeker.com)
# @File    : jssdkerror.py
# @DES     :

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response


class JSSDKErrorHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def post(self):
        """记录微信 js 调用错误信息"""

        self.logger.error("[JSSDKErrorHandler]wechat_id:{0}, wx_js_sdkerror:{1}, wx_js_sdk_config: {2}".format(
            self.current_user.wechat.id, self.json_args.get("jssdk_error"), self.json_args.get("jssdk_config")))
        self.log_info = {
            "jssdk_error": self.json_args.get("jssdk_error"),
        }

        self.send_json_success()
