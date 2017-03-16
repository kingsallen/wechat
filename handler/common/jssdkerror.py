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

        self.log_info({
            "jserror": self.json_args['jssdk_error']
        })
        self.logger.error("[JSSDKErrorHandler]wx_js_sdkerror:{}".format(self.json_args['jssdk_error']))

        self.send_json_success()
