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
        """是否需要弹出 仟寻隐私协议 窗口
        """
        user_id = 0 if user_id is None else user_id
        result, data = yield self.infra_privacy_ds.if_privacy_agreement_window(user_id)
        return result, data

    @gen.coroutine
    def if_agree_privacy(self, user_id, status):
        """是否同意 仟寻隐私协议"""
        result = yield self.infra_privacy_ds.if_agree_privacy(user_id, status)
        return result

    @gen.coroutine
    def if_custom_privacy_window(self, user_id, company_id):
        """是否需要弹出 客户自定义隐私协议 窗口
        """
        user_id = 0 if user_id is None else user_id
        ret = yield self.infra_privacy_ds.if_custom_privacy_window(user_id, company_id)
        return ret

    @gen.coroutine
    def get_custom_privacy_info(self, company_id):
        """获取客户自定义隐私协议信息
        """
        ret = yield self.infra_privacy_ds.get_custom_privacy_info(company_id)
        return ret

    @gen.coroutine
    def if_agree_custom_privacy(self, user_id, company_id):
        """是否同意 客户自定义隐私协议"""
        result = yield self.infra_privacy_ds.if_agree_custom_privacy(user_id, company_id)
        return result
