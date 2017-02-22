# coding=utf-8

from tornado import gen
from service.page.base import PageService

from thrift_gen.gen.useraccounts.service.UseraccountsServices import Client as UseraccountsServiceClient
from thrift_gen.gen.employee.service.EmployeeService import Client as EmployeeServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class EmployeePageService(PageService):

    employee_service_cilent = ServiceClientFactory.get_service(
        EmployeeServiceClient, "employee", CONF)
    useraccounts_service_cilent = ServiceClientFactory.get_service(
        UseraccountsServiceClient, "useraccounts", CONF)

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):
        ret = yield self.employee_service_cilent.getEmployeeRewards(
            employeeId=employee_id, companyId=company_id)
        raise gen.Return(ret)

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):
        ret = yield self.employee_service_cilent.unbind(
            employeeId=employee_id, companyId=company_id, userId=user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def bind(self, binding_params):
        ret = yield self.employee_service_cilent.bind(binding_params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_records(self,  user_id, page_no, page_size):
        """
        推荐记录，调用 thrify 接口
        :param app_id:
        :param user_id:
        :return:
        """
        ret = yield self.useraccounts_service_cilent.listRecommendation(
            userId=user_id, pageNo=page_no, pageSize=page_size)
        raise gen.Return(ret)
