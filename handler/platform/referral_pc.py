# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.base import BaseHandler, MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from handler.platform.referral import ReferralProfileAPIHandler, EmployeeRecomProfileHandler
from setting import settings


class ReferralLoginHandler(MetaBaseHandler):
    """pc端推荐简历登录页"""
    @handle_response
    @gen.coroutine
    def get(self):
        appid = settings['open_app_id']
        scope = "snsapi_login"
        redirect_url = self.make_url(path.REFERRAL_UPLOAD_PC, self.params, host=settings['referral_host'], wechat_signature=settings['qx_signature'])
        self.render_page(template_name="employee/pc-qrcode-login.html", data=ObjectDict({
            "wx_login_args": ObjectDict(appid=appid,
                                        scope=scope,
                                        redirect_uri=redirect_url)
        }))


class ReferralUploadHandler(BaseHandler):
    """pc端推荐简历页面"""
    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        ret = self.redis.get(const.UPLOAD_RECOM_PROFILE.format(self.current_user.sysuser.id))
        if ret:
            pid = ret.get("pid")
            data = yield self.employee_ps.get_referral_position_info(self.current_user.sysuser.id, pid)
            if data:
                reward = yield self.employee_ps.get_bind_reward(self.current_user.company.id, const.REWARD_UPLOAD_PROFILE)
                url = self.make_url(path.REFERRAL_PROFILE_PC, float=1)
                logo = self.current_user.company.logo
                qrcode = yield self.employee_ps.get_referral_qrcode(url, logo)
                data.update(reward_point=reward, wechat=ObjectDict({"qrcode": qrcode.data}))
                self.render_page(template_name="employee/pc-upload-resume.html", data=data)
                return
        self.logger.warning("[referral profile]get referral position info fail!")
        self.render_page(template_name="employee/pc-invalid-qrcode.html", data=None)


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
