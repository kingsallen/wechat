# coding=utf-8

from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
from util.common.exception import InfraOperationError



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
            return True
        # 如果不存在，创建 user_workwx 记录，返回 user_id
        workwx_userinfo.update({"company_id": company_id})
        workwx_userinfo.update({"work_wechat_userid": workwx_userinfo.userid})

        create_workwx = yield self.workwx_ds.create_workwx_user(ObjectDict(workwx_userinfo))
        if create_workwx.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(create_workwx.message)
        return create_workwx.get('data')


    @gen.coroutine
    def get_workwx_user(self, company_id, workwx_userid):
        """通过userid获取企业微信成员信息"""
        params = ObjectDict({
            "company_id": company_id,
            "work_wechat_userid": workwx_userid
        })
        ret = yield self.workwx_ds.get_workwx_user(params)
        return ret.data

    @gen.coroutine
    def get_workwx_user_by_sysuser_id(self, sysuser_id, company_id = None):
        """通过sysuser_id获取企业微信成员信息"""
        params = ObjectDict({
            "company_id": company_id,
            "sysuser_id": sysuser_id
        })
        ret = yield self.workwx_ds.get_workwx_user_by_sysuser_id(params)
        return ret.data

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
            "sysuserId": int(sysuser_id),
            "workwxUserid": workwx_userid,
            "companyId": int(company_id)
        })
        ret = yield self.workwx_ds.bind_workwx_qxuser(params)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        return ret

    @gen.coroutine
    def employee_bind(self, sysuser_id, company_id):
        """员工认证"""
        ret = yield self.workwx_ds.employee_bind(sysuser_id, company_id)
        return ret
