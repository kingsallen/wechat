# coding=utf-8


from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated

from thrift_gen.gen.employee.service.EmployeeService import Client as EmployeeServiceClient

from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF
from thrift.Thrift import TException


class AwardsHandler(BaseHandler):

    employee_service_cilent = ServiceClientFactory.get_service(
        EmployeeServiceClient, "employee", CONF)

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        rewards = []
        reward_configs = []
        total = 0
        is_binded = bool(self.current_user.employee)

        if is_binded:
            try:
                result = yield self.employee_service_cilent.getEmployeeRewards(
                    self.current_user.employee.id, self.current_user.company.id)
            except TException as te:
                self.logger.error(te)
                raise
            else:
                rewards = result.rewards
                reward_configs = result.reward_configs
                total = result.total

        self.render(
            "weixin/employee/reward.html",
            rewards=rewards,
            reward_configs=reward_configs,
            total=total,
            binded=is_binded,
            email_activation_state=0 if is_binded else \
                self.current_user.employee.activation)


