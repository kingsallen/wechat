# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.17

"""

from tornado import gen

from service.page.base import PageService


class CellphonePageService(PageService):
    """
    Referenced Document: https://wiki.moseeker.com/user_account_api.md
                         Point 32, 33
    """

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def send_valid_code(self, mobile, type, country_code=86):
        """Request basic service send valid code to target mobile
        :param mobile: target mobile number
        :return:
        """
        ret = yield self.infra_user_ds.post_send_valid_code(country_code, mobile, type)
        raise gen.Return(ret)

    @gen.coroutine
    def send_voice_code_for_register(self, mobile):
        """Request basic service to send voice code for register
        :param mobile:
        :return:
        """
        ret = yield self.infra_user_ds.post_send_voice_code_for_register(mobile)
        raise gen.Return(ret)

    @gen.coroutine
    def verify_mobile(self, country_code, mobile, code, type):
        """
        Send code submitted by user to basic service.
        :param country_code: 国家编号
        :param mobile: target mobile number
        :param code:
        :param type
        :return:
        """
        ret = yield self.infra_user_ds.post_verify_mobile(country_code, mobile, code, type)
        raise gen.Return(ret)

    @gen.coroutine
    def wx_pc_combine(self, country_code, mobile, unionid):
        """调用账号绑定接口"""
        ret = yield self.infra_user_ds.post_wx_pc_combine(
            country_code=country_code,
            mobile=mobile,
            unionid=unionid)
        raise gen.Return(ret)

    @gen.coroutine
    def send_sms(self, sms_type, mobile, params, isqx=False, ip=""):
        """
        发送短信，调用 thrift 接口
        :param sms_type: 对应 thrift_gen/gen/mq/struct/ttypes
        :param mobile:
        :param params:
        :param isqx: 是否为聚合号
        :return:
        """

        ret, msg = yield self.thrift_mq_ds.send_sms(sms_type, mobile, params, isqx, ip)
        return ret, msg


    @gen.coroutine
    def wx_change_mobile(self, country_code, mobile, user_id, unionid):
        """调用账号修改手机接口"""
        ret = yield self.infra_user_ds.post_wx_change_mobile(
            country_code=country_code,
            mobile=mobile,
            user_id=user_id,
            unionid=unionid)
        raise gen.Return(ret)
