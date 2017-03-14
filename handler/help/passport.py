# coding=utf-8

# @Time    : 3/14/17 17:29
# @Author  : panda (panyuxin@moseeker.com)
# @File    : passport.py
# @DES     :


from tornado import gen

import conf.message as msg
import conf.common as const
from handler.base import BaseHandler
from util.common import ObjectDict
from util.tool.str_tool import password_crypt
from util.common.decorator import handle_response, authenticated, verified_mobile_oneself
from oauth.wechat import WechatUtil
from thrift_gen.gen.mq.struct.ttypes import SmsType

class RegisterHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self, method):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, "get_" + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):

        self._event = self._event + "register"

        try:
            self.guarantee("company_name", "mobile")
        except:
            return

        hr_info = yield self.user_ps.get_hr_info_by_mobile(self.params.mobile)
        if hr_info:
            self.send_json_error(message=msg.HELPER_HR_REGISTERED)
            return

        params = ObjectDict(
            name=self.params.company_name,
            source=8 if self.in_wechat else 6,
        )
        result, res = yield self.company_ps.create_company_on_wechat(params)
        if not result:
            self.send_json_error(message=res.message)
            return

        code, passwd = password_crypt()
        data = ObjectDict({
            'mobile': self.params.mobile,
            'password': passwd,
            'wxuser_id': self.current_user.wxuser.id,
            'source': self.params.source,
            'last_login_ip': self.request.remote_ip,
            'register_ip': self.request.remote_ip,
            'auth_level': 0,
            'login_count': 0
        })
        res = yield self.user_ps.post_hr_register(data)
        if res.status != const.API_SUCCESS:
            self.send_json_error(message=res.message)
            return

        # 发送短信
        params = ObjectDict({
            "mobile": self.params.mobile,
            "code": code,
            "ip": self.request.remote_ip,
            "sys": 2 if self.is_qx else 1
        })
        yield self.cellphone_ps.send_sms(SmsType.EMPLOYEE_MERGE_ACCOUNT_SMS, self.params.mobile,
                                                          params)

        self.send_json_success()

    @handle_response
    @authenticated
    @gen.coroutine
    def get_register(self):

        self.render("weixin/sysuser/hr_register.html")

    @handle_response
    @verified_mobile_oneself
    @authenticated
    @gen.coroutine
    def get_qrcode(self):
        """
        获得专属二维码
        :return:
        """

        scene_str = "{0}_{1}_0".format(self.params.hr_id, self.current_user.wxuser.id)
        qrcode = WechatUtil.get_qrcode(self.current_user.wechat.access_token, scene_str)
        self.render("weixin/sysuser/wx_recruit_success.html", qrcodeurl=qrcode)








