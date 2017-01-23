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

    @gen.coroutine
    def send_valid_code(self, mobile):
        """Request basic service send valid code to target mobile
        :param mobile: target mobile number
        :return:
        """
        ret = yield self.infra_user_ds.post_send_valid_code(mobile)
        raise gen.Return(ret)

    @gen.coroutine
    def verify_mobile(self, params):
        """
        Send code submitted by user to basic service.
        :param params: dict include user mobile number and valid code
        :return:
        """
        ret = yield self.infra_user_ds.post_verify_mobile(params)
        raise gen.Return(ret)

    @gen.coroutine
    def wx_pc_combine(self, mobile, unionid):
        """调用账号绑定接口"""
        ret = yield self.infra_user_ds.post_wx_pc_combine(mobile, unionid)
        raise gen.Return(ret)
