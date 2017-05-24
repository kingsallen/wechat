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

        company_id = yield self.company_ps.create_company(params)
        if not company_id:
            self.send_json_error(message=msg.HELPER_HR_REGISTERED_FAILED)
            return

        code, passwd = password_crypt()
        data = ObjectDict({
            'mobile': self.params.mobile,
            'company_id': int(company_id),
            'password': passwd,
            'wxuser_id': self.current_user.wxuser.id,
            'source': int(self.params.source or 4),
            'last_login_ip': self.request.remote_ip,
            'register_ip': self.request.remote_ip,
            'login_count': 0
        })

        hr_id = yield self.user_ps.post_hr_register(data)
        if not hr_id:
            self.send_json_error(message=msg.HELPER_HR_REGISTERED)
            return

        # 必须创建 hr_company_accounts 对应关系表，否则 hr 平台会报错
        yield self.company_ps.create_company_accounts(company_id, hr_id)
        # hr_company 必须绑定 hr_id
        yield self.company_ps.update_company(conds={
            "id": company_id
        }, fields={
            "hraccount_id": hr_id
        })

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
