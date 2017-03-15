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
    def send_valid_code(self, mobile, type):
        """Request basic service send valid code to target mobile
        :param mobile: target mobile number
        :return:
        """
        ret = yield self.infra_user_ds.post_send_valid_code(mobile, type)
        raise gen.Return(ret)

    @gen.coroutine
    def verify_mobile(self, mobile, code, type):
        """
        Send code submitted by user to basic service.
        :param mobile: target mobile number
        :param code:
        :param type
        :return:
        """
        ret = yield self.infra_user_ds.post_verify_mobile(mobile, code, type)
        raise gen.Return(ret)

    @gen.coroutine
    def wx_pc_combine(self, mobile, unionid):
        """调用账号绑定接口"""
        ret = yield self.infra_user_ds.post_wx_pc_combine(mobile, unionid)
        raise gen.Return(ret)

    @gen.coroutine
    def send_sms(self, type, mobile, params, isqx=False, ip=""):
        """
        发送短信，调用 thrift 接口
        :param type: 对应 thrift_gen/gen/mq/struct/ttypes
        :param mobile:
        :param params:
        :param isqx: 是否为聚合号
        :return:
        """

        sys = 2 if isqx else 1
        ret = yield self.thrift_mq_ds.send_sms(type, mobile, params, sys, ip)
        self.logger.debug("[send_sms]ret:{}".format(ret))
        result = bool(ret.status == self.constant.API_SUCCESS)
        return result, ret.message
