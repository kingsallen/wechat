# coding=utf-8

import pprint

from thrift.Thrift import TException
from tornado import gen

from conf.common import YES, NO, OLD_YES
from handler.base import BaseHandler

from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated


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
            rewards_response = yield self.employee_ps.get_employee_rewards(
                self.current_user.employee.id,
                self.current_user.company.id)
            rewards = rewards_response.rewards
            reward_configs = rewards_response.rewardCofnigs
            total = rewards_response.total
        else: pass  # 使用初始化数据

        # 构建输出数据格式
        res_award_rules = []
        for rc in reward_configs:
            e = ObjectDict()
            e.name = rc.statusName
            e.point = rc.points
            res_award_rules.append(e)

        email_activation_state = OLD_YES if binded \
            else self.current_user.employee.activation

        res_rewards = []
        for rc in rewards:
            e = ObjectDict()
            e.reason = rc.reason
            e.hptitle = rc.title
            e.title = rc.title
            e.create_time = rc.updateTime
            e.point = rc.points
            res_rewards.append(e)
        # 构建输出数据格式完成

        self.send_json_success({
            'rewards': res_rewards,
            'award_rules': res_award_rules,
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
    /m/api/employee/binding"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        # 先获取员工认证配置信息
        conf_response = yield self.employee_ps.get_employee_conf(
            self.current_user.company.id)
        if not conf_response.exists:
            self.send_json_error("no employee conf")
        else:
            pass

        # 根据 conf 来构建 api 的返回 data
        data = yield self.employee_ps.make_binding_render_data(
            self.current_user, conf_response.employeeVerificationConf)
        self.logger.debug(pprint.pformat(data))
        self.send_json_success(data=data)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        binding_params = self.employee_ps.make_bind_params(
            self.current_user.sysuser.id, self.current_user.company.id,
            self.json_args)

        if not self.current_user.employee:
            result, message = yield self.employee_ps.bind(binding_params)
            if result:
                self.send_json_success()
                print(1111111111111111)
            else:
                self.send_json_error(message=message)
                print(222222222222222)
        else:
            self.send_json_error(message='binded')
            print(444444444444444)


class EmployeeBindEmailHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        pass


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
