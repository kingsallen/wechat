# coding=utf-8


from thrift.Thrift import TException
from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from thrift_gen.gen.employee.struct.ttypes import BindingParams
from util.common.decorator import handle_response, authenticated
from util.common import ObjectDict
from conf.common import YES, NO, OLD_YES


class AwardsHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        # 一些初始化的工作
        rewards = []
        reward_configs = []
        total = 0

        # 判断是否已经绑定员工
        binded = YES if self.current_user.employee else NO

        if binded:
            # 获取绑定员工
            result = yield self.employee_ps.get_employee_rewards(
                self.current_user.employee.id, self.current_user.company.id)
            rewards = result.rewards
            reward_configs = result.reward_configs
            total = result.total
        else:
            # 使用初始化数据
            pass

        # 构建输出数据格式
        award_rules = []
        for rc in reward_configs:
            e = ObjectDict()
            e.name = rc.statusName
            e.point = rc.points
            award_rules.append(e)

        email_activation_state = OLD_YES if binded \
            else self.current_user.employee.activation

        res_rewards = []
        for rc in rewards:
            e = ObjectDict()
            e.reason = rc.reason
            e.hptitle = rc.title
            e.title = rc.title
            e.create_time = rc.updateTime
            e.points = rc.point
            res_rewards.append(e)
        # 构建输出数据格式完成



        self.send_json_success(data={
            'rewards': rewards,
            'award_rules': award_rules,
            'point_total': total,
            'binded': binded,
            'email_activation_state': email_activation_state
        })


class EmployeeUnbindHandler(BaseHandler):
    """员工解绑 API"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        if self.current_user.employee:
            try:
                result = yield self.employee_ps.unbind(
                    self.current_user.employee.id,
                    self.current_user.company.id,
                    self.current_user.sysuser.id
                )
            except TException as te:
                self.logger.error(te)
                raise
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
            try:
                result = yield self.employee_ps.bind(binding_params)
            except TException as te:
                self.logger.error(te)
                raise
            if result:
                self.send_json_success()
                return
        self.send_json_error()


class RecommendrecordsHandler(BaseHandler):
    """员工-推荐记录"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        page_no = self.params.page_no or 0
        page_size = self.params.page_size or 10
        req_type = self.params.type or 1
        res = yield self.employee_ps.get_recommend_records(self.current_user.sysuser.id, req_type, page_no, page_size)
        self.send_json_success(data=res)
