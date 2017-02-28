# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.employee.service.EmployeeService import Client as EmployeeServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class ThriftEmployeeDataService(DataService):

    """对接 employee 的 thrift 接口
    """

    employee_service_cilent = ServiceClientFactory.get_service(
        EmployeeServiceClient, CONF)

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):
        ret = yield self.employee_service_cilent.getEmployeeRewards(employee_id, company_id)
        self.logger.debug("[thrift]get_employee_rewards: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):
        ret = yield self.employee_service_cilent.unbind(employee_id, company_id, user_id)
        self.logger.debug("[thrift]unbind: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def bind(self, binding_params):
        ret = yield self.employee_service_cilent.bind(binding_params)
        self.logger.debug("[thrift]bind: %s" % ret)
        raise gen.Return(ret)