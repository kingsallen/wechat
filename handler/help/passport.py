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
from util.common.decorator import handle_response, authenticated
from oauth.wechat import WechatUtil
from thrift_gen.gen.mq.struct.ttypes import SmsType

class RegisterQrcodeHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        """
        获得专属二维码
        :return:
        """

        scene_str = "{0}_{1}_0".format(self.params.hr_id, self.current_user.wxuser.id)
        qrcode = yield WechatUtil.get_qrcode(self.current_user.wechat.access_token, scene_str)
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

        hr_info = yield self.user_ps.get_hr_info_by_mobile(self.params.mobile)
        if hr_info:
            self.send_json_error(message=msg.HELPER_HR_HAD_REGISTERED)
            return

        params = ObjectDict(
            name=self.params.company_name,
            source=8 if self.in_wechat else 6,
        )

        is_ok, res_company = yield self.company_ps.create_company_on_wechat(params)
        if not is_ok:
            self.send_json_error(message=res_company.message)
            return

        code, passwd = password_crypt()
        data = ObjectDict({
            'mobile': self.params.mobile,
            'company_id': int(res_company),
            'password': passwd,
            'wxuser_id': self.current_user.wxuser.id,
            'source': int(self.params.source),
            'last_login_ip': self.request.remote_ip,
            'register_ip': self.request.remote_ip,
            'login_count': 0
        })

        hr_id = yield self.user_ps.post_hr_register(data)
        if not hr_id:
            self.send_json_error(message=msg.HELPER_HR_REGISTERED)
            return

        self.send_json_success(data={
            "hr_id": hr_id
        })

        # 发送短信
        params = {
            "mobile": self.params.mobile,
            "code": code,
        }
        yield self.cellphone_ps.send_sms(SmsType.EMPLOYEE_MERGE_ACCOUNT_SMS, self.params.mobile,
                                                          params, ip=self.request.headers.get('Remoteip'))
