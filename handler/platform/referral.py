# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated, check_employee_common

from util.wechat.core import get_temporary_qrcode


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
        self.render_page(template_name="employee/mobile-upload-resume.html", data=ObjectDict({"points": reward,
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
        yield self._post(type=1)

    @handle_response
    @gen.coroutine
    def _post(self, type=1):
        name = self.json_args.name
        mobile = self.json_args.mobile
        recom_reason = self.json_args.recom_reason
        pid = self.json_args.pid
        res = yield self.employee_ps.update_recommend(self.current_user.employee.id, name, mobile, recom_reason, pid, type)
        if res.status == const.API_SUCCESS:
            self.send_json_success(data=ObjectDict({
                "rid": res.data
            }))
        else:
            self.send_json_error()


class EmployeeRecomProfileHandler(BaseHandler):
    """上传简历"""

    @handle_response
    @gen.coroutine
    def post(self):
        yield self._post()

    @handle_response
    @gen.coroutine
    def _post(self):
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

        ret = yield self.emplyee_ps.upload_recom_profile(file_data, self.current_user.employee.id)
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
        wechat = yield self.wechat_ps.get_wechat_info(self.current_user, pattern_id=const.QRCODE_REFERRAL_CONFIRM, in_wechat=self.in_wechat)
        rid = self.params.rid
        ret = yield self.employee_ps.get_referral_info(rid)

        data = ObjectDict({
            "type": type,
            "variants": {
                "presentee_first_name": ret.employee_name,
                "recom_name": ret.user_name[0:1] + "**",
                "company_name": ret.company_abbreviation,
                "position_title": ret.position,
                "new_user": ret.user_name[0:1] + "**",
                "apply_id": ret,
                "mobile": ret.mobile[0:3] + "****" + ret.mobile[-4:],
                "wechat": wechat}
        })
        self.render_page(template_name="employee/recom-presentee-confirm.html", data=data)

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
            ret = yield self.employee_ps.confirm_referral_info(data)
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
        pid = self.params.pid
        reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
        yield self.employee_ps.update_referral_position(self.current_user.employee.id, pid)
        self.render_page(template_name="employee/recom-scan-qrcode.html", data=reward)


class ReferralCrucialInfoHandler(BaseHandler):
    """关键信息推荐"""

    @handle_response
    @authenticated
    @check_employee_common
    @gen.coroutine
    def get(self):
        pid = self.params.pid
        position_info = yield self.position_ps.get_position(pid)
        title = position_info.title
        self.params.share = yield self._make_share()
        self.render_page(template_name="employee/recom-candidate-info.html", data=ObjectDict({
            "job_title": title
        }))

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


class ReferralCrucialInfoApiHandler(BaseHandler):
    """提交关键信息"""
    @handle_response
    @gen.coroutine
    def post(self):
        ret = yield self.employee_ps.update_referral_crucial_info(self.current_user.employee.id, self.params)
        if ret.status != const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return
        else:
            self.send_json_success(data=ObjectDict({
                "rid": ret.data
            }))
            return



