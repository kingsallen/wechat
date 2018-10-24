# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from tornado.testing import AsyncTestCase, gen_test

from thrift_gen.gen.employee.service.EmployeeService import \
    Client as EmployeeServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory

from thrift_gen.gen.employee.struct.ttypes import Timespan


class ThriftEmployeeDataService(DataService):
    employee_service_cilent = ServiceClientFactory.get_service(
        EmployeeServiceClient)

    @gen.coroutine
    def get_employee_verification_conf(self, company_id):
        ret = yield self.employee_service_cilent.getEmployeeVerificationConf(
            company_id)
        return ret

    @gen.coroutine
    def set_employee_custom_info_email_pending(self, user_id, company_id,
                                               custom_values):
        ret = yield self.employee_service_cilent.setCacheEmployeeCustomInfo(
            int(user_id), int(company_id), str(custom_values))
        return ret

    @gen.coroutine
    def set_employee_custom_info(self, employee_id, custom_values):
        ret = yield self.employee_service_cilent.setEmployeeCustomInfo(
            int(employee_id), str(custom_values))
        return ret

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id, page_number,
                             page_size):
        ret = yield self.employee_service_cilent.getEmployeeRewards(
            employee_id, company_id, page_number, page_size)
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
    def activate_email(self, activation_code, bind_email_source):
        ret = yield self.employee_service_cilent.emailActivation(
            activation_code, bind_email_source)
        return ret

    @gen.coroutine
    def get_employee(self, user_id, company_id):
        ret = yield self.employee_service_cilent.getEmployee(user_id,
                                                             company_id)
        return ret

    @gen.coroutine
    def get_award_ranking(self, employee_id, company_id, type, page_from=0, page_size=20):
        """
        调用基础服务 thrift 接口 获取员工积分榜数据
        :param employee_id:
        :param company_id:
        :param type:
        :return:
        """
        type_conversion = {
            'month':   Timespan.month,
            'quarter': Timespan.quarter,
            'year':    Timespan.year
        }

        ret = yield self.employee_service_cilent.awardRanking(
            int(employee_id), int(company_id), type_conversion[type], page_from, page_size
        )
        return ret


class TestEmployeeService(AsyncTestCase):
    """Just for test(or try results) during development :)"""

    def setUp(self):
        self.employee_service_cilent = ServiceClientFactory.get_service(
            EmployeeServiceClient)
        super().setUp()

    @gen_test
    def test1(self):
        ret = yield self.employee_service_cilent.getEmployeeVerificationConf(1)
        print(ret)
        ret = yield self.employee_service_cilent.getEmployee(4, 1)
        print(ret)
