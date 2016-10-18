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
    def get_wxuser(self, openid, wechat_id):
        ret = yield self.user_wx_user_ds.get_wxuser(
            conds={
                "openid":    openid,
                "wechat_id": wechat_id
            })
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee(self, wxuser_id, company_id):
        res = yield self.user_employee_ds.get_employee(
            conds={
                "wxuser_id":  wxuser_id,
                "company_id": company_id,
                "disable":    "0",
                "activation": "0",
                "status":     "0"
            })
        raise gen.Return(res)

    @gen.coroutine
    def get_user_user(self, user_id):
        res = yield self.user_user_ds.get_user(
            conds={
                "id": user_id
            })
        raise gen.Return(res)



    # @gen.coroutine
    # def create_or_update_wxuser(self, userinfo, wechat_id):
    #     # 1. 按照userinfo.openid 和 wechat_id 尝试获取 wxuser
    #     wxuser = yield self.user_wx_user_ds.get_wxuser(openid=userinfo.openid, wechat_id=wechat_id)
    #     # 2. 如果没有 新建
    #     # 3. 如果有 更新
    #     if not wxuser:
    #         yield self.user_wx_user_ds.create_wxuser(userinfo, wechat_id)
    #     else:
    #         yield self.user_wx_user_ds.update_wxuser(userinfo, wechat_id)
