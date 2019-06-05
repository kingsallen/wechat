# coding=utf-8

from tornado import gen
from service.page.base import PageService


class PrivacyPageService(PageService):
    """
    隐私协议 弹窗服务
    """

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def if_privacy_agreement_window(self, user_id):
        """是否需要弹出 隐私协议 窗口
        """
        user_id = 0 if user_id is None else user_id
        result, data = yield self.infra_privacy_ds.if_privacy_agreement_window(user_id)
        return result, data

    @gen.coroutine
    def if_agree_privacy(self, user_id, status):
        """是否同意 隐私协议"""
        result, data = yield self.infra_privacy_ds.if_agree_privacy(user_id, status)
        return result, data
