# coding=utf-8

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response
from conf.common import *


class SwitchHandler(BaseHandler):
    """开关方法"""

    @handle_response
    @gen.coroutine
    def get(self, method):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'get_' + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def post(self, method):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'post_' + method)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def post_popup_window(self):
        """
        职位详情页关闭弹窗
        params: df_pv_qrcode: 关闭qrcode弹窗  type:0
                df_pv_profile: 关闭简历完善引导弹层   type：1
        """
        if self.json_args.get('df_pv_qrcode'):
            yield self.user_ps.close_popup_window(
                self.current_user.sysuser.id,
                self.current_user.company.id,
                REFERRAL_CLOSE_QRCODE)
        elif self.json_args.get('df_pv_profile'):
            yield self.user_ps.close_popup_window(
                self.current_user.sysuser.id,
                self.current_user.company.id,
                REFERRAL_CLOSE_PROFILE)
        self.send_json_success()

    @gen.coroutine
    @handle_response
    def get_radar(self):
        """
        获取人脉雷达模块是否开启
        :return:
        """
        ret = yield self.company_ps.check_radar_switch_status(self.current_user.company.id)
        if not ret.status == API_SUCCESS:
            self.send_json_error(message=ret.message)

        self.send_json_success(data=ret.data[0].get('valid'))
