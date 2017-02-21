# coding=utf-8


from thrift.Thrift import TException
from tornado import gen

from handler.base import BaseHandler
from thrift_gen.gen.employee.struct.ttypes import BindingParams
from util.common.decorator import handle_response, authenticated


class AwardsHandler(BaseHandler):

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
                result = yield self.employee_ps.get_employee_rewards(
                    self.current_user.employee.id, self.current_user.company.id
                )
            except TException as te:
                self.logger.error(te)
                raise
            else:
                rewards = result.rewards
                reward_configs = result.reward_configs
                total = result.total

        # todo (tangyiliang) 前端渲染
        self.render(
            "refer/weixin/employee/reward.html",
            rewards=rewards,
            reward_configs=reward_configs,
            total=total,
            binded=is_binded,
            email_activation_state=0 if is_binded else self.current_user.employee.activation)


class EmployeeUnbindHandler(BaseHandler):
    """员工解绑 API"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        if self.current_user.employee:
            result = yield self.employee_ps.unbind(
                self.current_user.employee.id,
                self.current_user.company.id,
                self.current_user.sysuser.id
            )
            if result:
                self.send_json_success()
                return

        self.send_json_error()


class EmployeeBindHandler(BaseHandler):
    """员工绑定 API
    /m/api/employee/bind"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        guarantee_list = [
            'name', 'mobile', 'custom_field', 'email', 'answer1', 'answer2',
            'type'
        ]
        self.guarantee(guarantee_list)

        # TODO (yiliang) 是否要强制验证 name 和 mobile 不为空？

        # 构建 bindingParams
        binding_params = BindingParams(
            type=self.params.type,
            userId=self.current_user.sysuser.id,
            companyId=self.current_user.company.id,
            email=self.params.email,
            mobile=self.params.mobile,
            customField=self.params.custom_field,
            name=self.params.name,
            answer1=self.params.answer1,
            answer2=self.params.answer2)

        if not self.current_user.employee:
            result = yield self.employee_ps.bind(binding_params)
            if result:
                self.send_json_success()
                return
        self.send_json_error()
