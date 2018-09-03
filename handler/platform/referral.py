# coding=utf-8

from tornado import gen

import conf.common as const
import conf.message as msg
import conf.fe as fe
import conf.message as messages
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str
from urllib import parse
import conf.platform as const_platform
from util.wechat.core import get_temporary_qrcode
import base64


class ReferralProfileHandler(BaseHandler):
    """微信端推荐人才简历"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        pid = self.params.pid
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        position_info = yield self.position_ps.get_position(pid)

        self.params.share = yield self._make_share()
        self.render_page(template_name="/employee/mobile-upload-resume.html", data=ObjectDict({"points": reward,
                                                                                               "job_title": position_info.title}))

    def _make_share(self):
        link = self.make_url(
            path.REFERRAL_CONFIRM,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id))

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)

        share_info = ObjectDict({
            "cover": cover,
            "title": "【#name#】恭喜您已被内部员工推荐",
            "description": "点击查看详情~",
            "link": link
        })
        return share_info


class ReferralProfileAPIHandler(BaseHandler):
    """微信端推荐人才简历api"""

    @handle_response
    @gen.coroutine
    def post(self):
        name = self.json_args.name
        mobile = self.json_args.mobile
        recom_reason = self.json_args.recom_reason
        pid = self.json_args.pid
        res = yield self.employee_ps.update_recommend(name, mobile, recom_reason)
        if res.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error()


class EmployeeRecomProfileHandler(BaseHandler):
    """上传简历"""

    @handle_response
    @gen.coroutine
    def post(self):
        if len(self.request.files) == 0:
            file_data = self.request.body
            file_name = self.get_argument("vfile")
        else:
            image = self.request.files["vfile"][0]
            file_data = image["body"]
            file_name = image["filename"]

        if len(file_data) > 2 * 1024 * 1024:
            self.send_json_error("请上传2M以下的文件")
            return

        ret = yield self.emplyee_ps.upload_recom_profile(file_name, file_data)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ret.data)
            return


class ReferralConfirmHandler(BaseHandler):
    """推荐成功"""

    @handle_response
    @gen.coroutine
    def get(self):
        if self.current_user.sysuser.username.isdigit():
            type = 1
        else:
            if self.current_user.wxuser.is_subscribe or self.current_user.wechat.type == 0:
                type = 2
            else:
                type = 3
        wechat = ObjectDict()
        wechat.subscribed = True if self.current_user.wxuser.is_subscribe else False
        wechat.qrcode = yield get_temporary_qrcode(wechat=self.current_user.wechat,
                                                   pattern_id=const.QRCODE_REFERRAL_CONFIRM)
        wechat.name = self.current_user.wechat.name
        rkey = self.params.rkey
        ret = yield self.employee_ps.get_referral_info(rkey)

        data = ObjectDict({
            "type": type,
            "variants": {
                "presentee_first_name": ret,
                "recom_name": ret,
                "company_name": ret,
                "position_title": ret,
                "new_user": ret,
                "apply_id": ret,
                "mobile": ret.mobile[0:3] + "****" + ret.mobile[-4:],
                "wechat": wechat}
        })
        self.render_page(template_name="", data=data)

        return


class ReferralConfirmApiHandler(BaseHandler):
    """推荐成功api"""

    @handle_response
    @gen.coroutine
    def post(self):
        if self.current_user.sysuser.username.isdigit():
            try:
                self.guarantee("name")
            except AttributeError:
                raise gen.Return()
            data = ObjectDict({
                "name": self.params.name
            })
            ret = yield self.update_referral_info(data)
        else:
            try:
                self.guarantee("mobile", "name", "vcode")
            except AttributeError:
                raise gen.Return()
            data = ObjectDict({
                "name": self.params.name,
                "mobile": self.params.mobile,
                "valid_code": self.params.valid_code
            })
            ret = yield self.update_referral_info(data)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ret.data)
            return


class ReferralProfilePcHandler(BaseHandler):
    """电脑扫码上传简历"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        self.render_page(template_name="", data=reward)
