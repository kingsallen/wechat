# coding=utf-8

from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict



class WorkwxPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def create_workwx_user(self, workwx_userinfo, company_id, workwx_userid):
        """
        根据微信授权得到的 userinfo 创建 企业微信成员信息：workwx_user
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
        """获取企业微信成员信息"""
        params = ObjectDict({
            "company_id": company_id,
            "workwx_userid": workwx_userid
        })
        ret = yield self.workwx_ds.get_workwx_user(params)
        return ret

    @gen.coroutine
    def get_workwx(self, company_id, hraccount_id):
        """获取企业微信配置"""
        params = ObjectDict({
            "companyId": company_id,
            "hraccountId": hraccount_id
        })
        ret = yield self.workwx_ds.get_workwx(params)
        return ret.data

    @gen.coroutine
    def bind_workwx_qxuser(self, sysuser_id, workwx_userid, company_id):
        """绑定企业微信成员和仟寻用户"""
        params = ObjectDict({
            "sysuser_id": sysuser_id,
            "workwx_userid": workwx_userid,
            "company_id": company_id
        })
        ret = yield self.workwx_ds.bind_workwx_qxuser(params)
        return ret

    @gen.coroutine
    def employee_bind(self, sysuser_id, company_id):
        """员工认证"""
        params = ObjectDict({
            "userId": sysuser_id,
            "companyId": company_id,
            "type": 3
        })
        ret = yield self.workwx_ds.employee_bind(params)
        return ret
