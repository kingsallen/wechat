# coding=utf-8

from tornado import gen

import conf.path as path
import conf.common as const
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
        binded = const.YES if self.current_user.employee else const.NO

        if binded:
            # 获取绑定员工
            rewards_response = yield self.employee_ps.get_employee_rewards(
                self.current_user.employee.id,
                self.current_user.company.id)
            rewards = rewards_response.rewards
            reward_configs = rewards_response.rewardConfigs
            total = rewards_response.total
        else:
            pass  # 使用初始化数据

        # 构建输出数据格式
        res_award_rules = []
        if reward_configs:
            for rc in reward_configs:
                e = ObjectDict()
                e.name = rc.statusName
                e.point = rc.points
                res_award_rules.append(e)

        email_activation_state = const.OLD_YES if binded \
            else self.current_user.employee.activation

        res_rewards = []
        if rewards:
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
            'rewards':                res_rewards,
            'award_rules':            res_award_rules,
            'point_total':            total,
            'binded':                 binded,
            'email_activation_state': email_activation_state
        })


class EmployeeUnbindHandler(BaseHandler):
    """员工解绑 API"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        if self.current_user.employee:
            result, message = yield self.employee_ps.unbind(
                self.current_user.employee.id,
                self.current_user.company.id,
                self.current_user.sysuser.id
            )
            self.logger.debug('*' * 80)
            self.logger.debug('unbind result: %s' % result)
            self.logger.debug('*' * 80)
            if result:
                self.send_json_success()
            else:
                self.send_json_error(message)
        else:
            self.send_json_error('unbind error')


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
        self.logger.debug(data)
        self.send_json_success(data=data)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        binding_params = self.employee_ps.make_bind_params(
            self.current_user.sysuser.id,
            self.current_user.company.id,
            self.json_args)
        self.logger.debug(binding_params)

        if not self.current_user.employee:
            result, message = yield self.employee_ps.bind(binding_params)
            self.logger.debug(result)
            self.logger.debug(message)
            if result:
                self.send_json_success(message=message)
                self.finish()

                # 处理员工认证红包
                yield self.redpacket_ps.handle_red_packet_employee_verification(
                    user_id=self.current_user.sysuser.id,
                    company_id=self.current_user.company.id,
                    redislocker=self.redis
                )
            else:
                self.send_json_error(message=message)
        else:
            self.send_json_error(message='binded')


class EmployeeBindEmailHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        activation_code = self.params.activation_code
        result, message = yield self.employee_ps.activate_email(
            activation_code)

        tparams = dict(
            qrcode_url=path.HR_WX_IMAGE_URL + self.current_user.wechat.qrcode,
            wechat_name=self.current_user.wechat.name
        )
        tname = 'success' if result else 'failure'

        self.render(template_name='employee/certification-%s.html' % tname,
                    **tparams)

        # 处理员工认证红包开始
        employee = yield self.user_employee_ds.get_employee({
            'activation_code': activation_code,
            'activation':      const.OLD_YES,
            'disable':         const.OLD_YES,
            'status':          const.OLD_YES
        })

        if result and employee:
            yield self.redpacket_ps.handle_red_packet_employee_verification(
                user_id=employee.sysuser_id,
                company_id=employee.company_id,
                redislocker=self.redis
            )
        # 处理员工认证红包结束


class RecommendrecordsHandler(BaseHandler):
    """员工-推荐记录"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        page_no = self.params.page_no or 0
        page_size = self.params.page_size or 10
        req_type = self.params.type or 1
        res = yield self.employee_ps.get_recommend_records(
            self.current_user.sysuser.id, req_type, page_no, page_size)
        self.send_json_success(data=res)
