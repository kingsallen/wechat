# coding=utf-8

from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict



class WorkWXPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def create_workwx_user(self, workwx_userinfo, company_id, workwx_userid):
        """
        根据微信授权得到的 userinfo 创建 workwx_user
        :param userid:
        :param wechat_id:
        :param remote_ip:
        :param source:
        """
        # 查询 这个 userid 是不是已经存在
        workwx_user_record = yield self.get_workwx_user(company_id, workwx_userid)

        # 如果存在，返回 userid
        if workwx_user_record:
            res = True
        else:
            # 如果不存在，创建 user_workwx 记录，返回 user_id
            workwx_userinfo.update({"company_id": company_id})
            params = ObjectDict({
                "workwx_userinfo": workwx_userinfo
            })
            create_workwx = yield self.workwx_ds.create_workwx_user(params)
            res = create_workwx.get('data')
        return res

    @gen.coroutine
    def get_workwx_user(self, company_id, workwx_userid):
        params = ObjectDict({
            "company_id": company_id,
            "workwx_userid": workwx_userid
        })
        ret = yield self.workwx_ds.get_workwx_user(params)
        return ret

    @gen.coroutine
    def get_workwx(self, company_id, hraccount_id):
        params = ObjectDict({
            "companyId": company_id,
            "hraccountId": hraccount_id
        })
        ret = yield self.workwx_ds.get_workwx(params)
        return ret

    @gen.coroutine
    def bind_workwx_qxuser(self, sysuser_id, workwx_userid, company_id):
        params = ObjectDict({
            "sysuser_id": sysuser_id,
            "workwx_userid": workwx_userid,
            "companyId": company_id
        })
        ret = yield self.workwx_ds.bind_workwx_qxuser(params)
        return ret
