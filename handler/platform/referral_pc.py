# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from handler.platform.referral import ReferralProfileAPIHandler, EmployeeRecomProfileHandler


class ReferralQrcodeHandler(BaseHandler):
    """pc端获取跳转二维码"""

    @handle_response
    @gen.coroutine
    def get(self):
        url = self.make_url(path.REFERRAL_PROFILE_PC, float=1)
        logo = self.current_user.company.logo
        ret = yield self.employee_ps.get_referral_qrcode(url, logo)
        if ret.status != const.API_SUCCESS:
            self.send_json_error()
        else:
            self.send_json_success(ret.data)


class ReferralLoginHandler(BaseHandler):
    """pc端推荐简历登录页"""
    @handle_response
    @gen.coroutine
    def get(self):
        redirect_url = self.make_url(path.REFERRAL_UPLOAD_PC, self.params)
        self.render_page(template_name="employee/pc-qrcode-login.html", data=ObjectDict({
            "redirect_url": redirect_url
        }))


class ReferralUploadHandler(BaseHandler):
    """pc端推荐简历页面"""
    @handle_response
    @gen.coroutine
    def get(self):
        pid = self.redis.get(const.UPLOAD_RECOM_PROFILE.format(self.current_user.sysuser.id))
        res, data = yield self.employee_ps.get_referral_position_info(self.current_user.employee.id, pid)
        if res.status != const.API_SUCCESS:
            self.logger.warning("[referral profile]get referral position info fail!")
            self.render(template_name="employee/pc-invalid-qrcode.html")
        else:
            reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
            data = res.data
            data.update(reward_point=reward)
            self.render_page(template_name="employee/pc-upload-resume.html", data=data)


class ReferralProfileAPIPcHandler(ReferralProfileAPIHandler):
    """pc端推荐简历提交推荐"""
    @handle_response
    @gen.coroutine
    def post(self):
        yield self._post(type=2)


class EmployeeRecomProfilePcHandler(EmployeeRecomProfileHandler):
    """pc端推荐上传简历"""

    @handle_response
    @gen.coroutine
    def post(self):
        self._post()
