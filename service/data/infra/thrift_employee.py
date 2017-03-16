# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from tornado.testing import AsyncTestCase, gen_test

from thrift_gen.gen.employee.service.EmployeeService import Client as EmployeeServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class ThriftEmployeeDataService(DataService):

    employee_service_cilent = ServiceClientFactory.get_service(
        EmployeeServiceClient, CONF)

    @gen.coroutine
    def get_employee_verification_conf(self, company_id):
        ret = yield self.employee_service_cilent.getEmployeeVerificationConf(company_id)
        return ret

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):
        ret = yield self.employee_service_cilent.getEmployeeRewards(
            employee_id, company_id)
        return ret

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):
        ret = yield self.employee_service_cilent.unbind(
            employee_id, company_id, user_id)
        return ret

    @gen.coroutine
    def bind(self, binding_params):
        ret = yield self.employee_service_cilent.bind(binding_params)
        return ret

    @gen.coroutine
    def get_employee(self, user_id, company_id):
        ret = yield self.employee_service_cilent.getEmployee(user_id, company_id)
        return ret


class TestEmployeeService(AsyncTestCase):
    """Just for test(or try results) during development :)"""
    def setUp(self):
        self.employee_service_cilent = ServiceClientFactory.get_service(
            EmployeeServiceClient, CONF)
        super().setUp()

    @gen_test
    def test1(self):
        ret = yield self.employee_service_cilent.getEmployeeVerificationConf(1)
        print(ret)
        ret = yield self.employee_service_cilent.getEmployee(4, 1)
        print(ret)
