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

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        self.params.share = yield self._make_share()
        self.render_page(template_name="", data=reward)

    def _make_share(self):
        link = self.make_url(
            path.REFERRAL_COMFIRM,
            self.params,
            recom=self.position_ps._make_recom(self.current_user.sysuser.id))

        company_info = yield self.company_ps.get_company(
            conds={"id": self.current_user.company.id}, need_conf=True)

        cover = self.share_url(company_info.logo)

        share_info = ObjectDict({
            "cover": cover,
            "title": "恭喜您已被内部员工推荐",
            "description": "点击查看详情~",
            "link": link
        })
        return share_info


class ReferralProfileAPIHandler(BaseHandler):

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

    @handle_response
    @gen.coroutine
    def post(self):
        if len(self.request.files) == 0:
            file_data = self.request.body
            file_name = self.get_argument("upload_file")
        else:
            image = self.request.files["upload_file"][0]
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

    @handle_response
    @gen.coroutine
    def get(self):
        rkey = self.params.rkey
        ret = yield self.employee_ps.get_referral_info(rkey)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            data = ret.data

            self.send_json_success(data=ObjectDict({
                "presentee_first_name": data,
                "recom_name": data,
                "company_name": data,
                "position_title": data,
                "new_user": data
            }))
            return
