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


class ReferralQrcodeHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        ret = yield self.employee_ps.get_referral_qrcode(self.current_user.wechat.id)
        if ret.status != const.API_SUCCESS:
            pass
        else:
            self.send_json_success(ret.data)


class ReferralLoginHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        redirect_url = self.make_url(path.REFERRAL_UPLOAD_PC, self.params)
        self.render_page(template_name="", data=ObjectDict({
            "redirect_url": redirect_url
        }))


class ReferralUploadHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        res, data = yield self.employee_ps.get_referral_position_info(self.current_user.sysuser.id)
        if res.status != const.API_SUCCESS:
            self.logger.warning("[referral profile]get referral position info fail!")
            self.render(template_name="")
        else:
            data = res.data
            self.render_page(template_name="", data=data)



