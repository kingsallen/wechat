# coding=utf-8

from tornado import gen
from service.page.base import PageService

from thrift_gen.gen.useraccounts.service.UserCenterService import Client as UsercenterServiceClient
from thrift_gen.gen.employee.service.EmployeeService import Client as EmployeeServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class EmployeePageService(PageService):

    employee_service_cilent = ServiceClientFactory.get_service(
        EmployeeServiceClient, "employee", CONF)
    usercenter_service_cilent = ServiceClientFactory.get_service(
        UsercenterServiceClient, "useraccounts", CONF)

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
    def get_recommend_records(self, user_id, type, page_no, page_size):
        """
        推荐历史记录，调用 thrify 接口
        :param user_id:
        :param type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.usercenter_service_cilent.getRecommendation(
            userId=user_id, type=type, pageNo=page_no, pageSize=page_size)
        raise gen.Return(ret)
