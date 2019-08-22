# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict
from util.wechat.core import get_temporary_qrcode, get_miniapp_code
import conf.common as const


class WechatPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_wechat(self, conds, fields=[]):

        """
        获得公众号信息
        :param conds:
        :param fields: 示例:
        conds = {
            "id": wechat_id
            "signature": signature
        }
        :return:
        """

        wechat = yield self.hr_wx_wechat_ds.get_wechat(conds, fields)

        raise gen.Return(wechat)

    @gen.coroutine
    def get_wechat_theme(self, conds, fields=[]):

        """
        获得公众号主题色信息
        :param conds:
        :param fields:
        :return:
        """

        theme = yield self.config_sys_theme_ds.get_theme(conds, fields)
        raise gen.Return(theme)

    @gen.coroutine
    def get_wechat_info(self, current_user, scene_id, in_wechat, action_name="QR_SCENE"):
        """
        获取公众号相关信息
        """
        wechat = ObjectDict()
        wechat.subscribed = True if not in_wechat or current_user.wechat.type == 0 or current_user.wxuser.is_subscribe else False
        wechat.qrcode = yield get_temporary_qrcode(wechat=current_user.wechat,
                                                   scene_id=scene_id, action_name=action_name)
        wechat.name = current_user.wechat.name
        return wechat

    @gen.coroutine
    def get_wechat_in_workwx(self, wechat, scene_id, action_name="QR_SCENE"):
        """
        获取公众号相关信息
        """
        wechat_in_workwx = ObjectDict()
        wechat_in_workwx.subscribed = False
        wechat_in_workwx.qrcode = yield get_temporary_qrcode(wechat=wechat, scene_id=scene_id, action_name=action_name)
        wechat_in_workwx.name = wechat.name
        return wechat_in_workwx

    @gen.coroutine
    def get_miniapp_code(self, scene_id):
        """
        获取小程序码
        :param scene_id:
        :return:
        """
        params = {
            "appid": self.settings['upload_resume_miniapp_appid'],
            "appSecret": self.settings['upload_resume_miniapp_app_secret'],
        }
        res = yield self.infra_profile_ds.infra_upload_miniapp_access(params)
        access_token = res.data.access_token
        buffer = yield get_miniapp_code(scene_id, access_token)
        return buffer
