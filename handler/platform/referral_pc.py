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
        user_info = yield self.employee_ps.get_employee_info_by_user_id(self.current_user.sysuser.id)
        pid = ret.get("pid") if ret else 0
        if pid and user_info:
            data = yield self.employee_ps.get_referral_position_info(user_info.employee_id, pid)
        else:
            data = ObjectDict()
        if data and user_info:
            reward = yield self.employee_ps.get_bind_reward(user_info.company.id, const.REWARD_UPLOAD_PROFILE)
            data.update(reward_point=reward)
            self.render_page(template_name="employee/pc-upload-resume.html", data=data)
        else:
            self.logger.warning("[referral profile]get referral position info fail!")
            self.render_page(template_name="employee/pc-invalid-qrcode.html", data=None)


class ReferralProfileAPIPcHandler(ReferralProfileAPIHandler):
    """pc端推荐简历提交推荐"""
    @handle_response
    @gen.coroutine
    def post(self):
        user_info = yield self.employee_ps.get_employee_info_by_user_id(self.current_user.sysuser.id)
        yield self._post(type=2, employee_id=user_info.employee_id)


class EmployeeRecomProfilePcHandler(EmployeeRecomProfileHandler):
    """pc端推荐上传简历"""

    @handle_response
    @gen.coroutine
    def post(self):
        user_info = yield self.employee_ps.get_employee_info_by_user_id(self.current_user.sysuser.id)
        yield self._post(employee_id=user_info.employee_id)
