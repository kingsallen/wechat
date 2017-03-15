# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService


class ThriftEmployeeDataService(DataService):

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):
        ret = yield self.employee_ps.getEmployeeRewards(employee_id, company_id)
        raise gen.Return(ret)

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):
        ret = yield self.employee_ps.unbind(employee_id, company_id, user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def bind(self, binding_params):
        ret = yield self.employee_ps.bind(binding_params)
        raise gen.Return(ret)
