# coding=utf-8

# @Time    : 3/14/17 17:29
# @Author  : panda (panyuxin@moseeker.com)
# @File    : passport.py
# @DES     :


from tornado import gen

import conf.message as msg
from handler.base import BaseHandler
from util.common import ObjectDict
from util.tool.str_tool import password_crypt
from util.wechat.core import get_qrcode
from util.common.decorator import handle_response, authenticated
from thrift_gen.gen.mq.struct.ttypes import SmsType


class RegisterQrcodeHandler(BaseHandler):

    # @handle_response
    # @authenticated
    @gen.coroutine
    def get(self):

        """
        获得专属二维码
        :return:
        """

        scene_str = "{0}_{1}_0".format(self.params.hr_id, self.current_user.wxuser.id)
        qrcode = yield get_qrcode(self.current_user.wechat.access_token, scene_str)

        self.render(template_name="refer/weixin/sysuser/wx_recruit_success.html", qrcodeurl=qrcode)


class RegisterHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):

        try:
            self.guarantee("company_name", "mobile")
        except:
            return

        params = ObjectDict(
            company_name=self.params.company_name,
            mobile=self.params.mobile,
            source=8 if self.in_wechat else 6,
            wxuser_id=self.current_user.wxuser.id,
            remote_id=self.request.remote_ip
        )

        status, message, body = yield self.company_ps.create_company(params)

        if status == 0:
            data = ObjectDict({
                'hr_id': body.hr_id
            })
            self.send_json_success(data=data, message=message)
        else:
            self.send_json_error(message=message)


