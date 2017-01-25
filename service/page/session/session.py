# coding=utf-8

from tornado import gen

from service.page.base import PageService


class SessionPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def get_wechat_by_signature(self, signature):
        ret = yield self.hr_wx_wechat_ds.get_wechat(
            conds={"signature": signature})
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee(self, user_id, company_id):
        res = yield self.user_employee_ds.get_employee(
            conds={
                "sysuser_id":  user_id,
                "company_id": company_id,
                "disable":    "0",
                "activation": "0",
                "status":     "0"
            })
        raise gen.Return(res)
