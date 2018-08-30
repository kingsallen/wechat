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
            "title": "【】恭喜您已被内部员工推荐",
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
        res = yield self.employee_ps.update_recommend(name, mobile, recom_reason)
        if res.status == const.API_SUCCESS:
            self.send_json_success()
        else:
            self.send_json_error()












