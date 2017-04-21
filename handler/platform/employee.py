# coding=utf-8

from tornado import gen

import conf.path as path
import conf.common as const
import conf.fe as fe
import conf.message as messages
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.tool.url_tool import make_url
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str


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
        infra_bind_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(infra_bind_status)

        if fe_bind_status in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS,
                              fe.FE_EMPLOYEE_BIND_STATUS_PENDING]:

            result, message = yield self.employee_ps.unbind(
                employee.id,
                self.current_user.company.id,
                self.current_user.sysuser.id
            )
            self.logger.debug('unbind result: %s' % result)
            self.logger.debug('unbind message: %s' % message)
            if result:
                self.send_json_success()
            else:
                self.send_json_error(message=message)
        else:
            self.send_json_error(message='not binded or pending')


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

        thrift_bind_status = yield self.employee_ps.get_employee_bind_status(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        fe_bind_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            thrift_bind_status)

        # early return 1
        if fe_bind_status == fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS:
            self.send_json_error(message=messages.EMPLOYEE_BINDED_WARNING)
            return

        result, result_message = yield self.employee_ps.bind(binding_params)
        self.logger.debug("bind_result: %s" % result)
        self.logger.debug("result_message: %s" % result_message)

        # early return 2
        if not result:
            self.send_json_error(message=result_message)
            return

        message = result_message
        refine_info_way = self.company_ps.emp_custom_field_refine_way(
            self.current_user.company.id)

        if refine_info_way == const.EMPLOYEE_CUSTOM_FIELD_REFINE_REDIRECT:
            next_url = make_url(path.EMPLOYEE_CUSTOMINFO,
                                self.params,
                                from_wx_template='x')

        elif refine_info_way == const.EMPLOYEE_CUSTOM_FIELD_REFINE_TEMPLATE_MSG:
            yield self.employee_ps.send_emp_custom_info_template(
                self.current_user)

            next_url = make_url(path.EMPLOYEE_BINDED, self.params)
        else:
            assert False  # should not be here

        self.logger.debug(next_url)
        self.logger.debug(message)
        self.send_json_success(
            data={'next_url': next_url},
            message=message
        )
        self.finish()

        # 处理员工认证红包
        yield self.redpacket_ps.handle_red_packet_employee_verification(
            user_id=self.current_user.sysuser.id,
            company_id=self.current_user.company.id,
            redislocker=self.redis
        )


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

        employee = yield self.employee_ps.get_valid_employee_record_by_activation_code(activation_code)

        if result and employee:
            # 处理员工认证红包开始
            yield self.redpacket_ps.handle_red_packet_employee_verification(
                user_id=employee.sysuser_id,
                company_id=employee.company_id,
                redislocker=self.redis
            )
            # 处理员工认证红包结束

            # 员工认证信息填写消息模板
            refine_info_way = self.company_ps.emp_custom_field_refine_way(
                self.current_user.company.id)

            if refine_info_way == const.EMPLOYEE_CUSTOM_FIELD_REFINE_TEMPLATE_MSG:
                yield self.employee_ps.send_emp_custom_info_template(
                    self.current_user)


class RecommendRecordsHandler(BaseHandler):
    """员工-推荐记录"""

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10
        req_type = self.params.type or 1
        res = yield self.employee_ps.get_recommend_records(
            self.current_user.sysuser.id, req_type, page_no, page_size)
        self.logger.debug("RecommendrecordsHandler:{}".format(res))
        self.send_json_success(data=res)


class CustomInfoHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        fe_binding_status = self.employee_ps.convert_bind_status_from_thrift_to_fe(
            binding_status)

        self.logger.debug('binding_status: %s' % binding_status)
        self.logger.debug('fe_binding_status: %s' % fe_binding_status)

        # unbinded users may not need to know this page
        if (fe_binding_status not in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS,
                                      fe.FE_EMPLOYEE_BIND_STATUS_PENDING]):
            self.write_error(404)
            return
        else:
            pass

        selects = yield self.employee_ps.get_employee_custom_fields(
            self.current_user.company.id)

        data = ObjectDict(
            selects=selects,
            from_wx_template=self.params.from_wx_template or "x",
            employee_id=employee.id,
            action_url=path.EMPLOYEE_CUSTOMINFO
        )

        self.render_page(
            template_name="employee/bind_success_info.html",
            data=data)

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        # unbinded users may not need to know this page
        if (self.employee_ps.convert_bind_status_from_thrift_to_fe(
            binding_status) not in [fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS,
                                    fe.FE_EMPLOYEE_BIND_STATUS_PENDING]):
            self.write_error(404)
        elif (str(employee.id) != self.params._employeeid or
                not self.params._employeeid):
            self.write_error(416)
        else:
            pass

        # 构建跳转 make_url 的 escape
        escape = ['headimg', 'next_url']
        keys = []
        for k, v in self.request.arguments.items():
            if k.startswith("key_"):
                escape.append(k)
                confid = int(k[4:])
                keys.append({confid: [to_str(v[0])]})

        self.logger.debug("keys: %s" % keys)
        custom_fields = json_dumps(keys)

        yield self.employee_ps.update_employee_custom_fields(employee.id, custom_fields)

        # 判断与跳转
        self.params.pop('next_url', None)
        self.params.pop('headimg', None)
        next_url = make_url(path.POSITION_LIST, self.params, escape=escape)

        if self.params.from_wx_template == "o":
            message = messages.EMPLOYEE_BINDING_CUSTOM_FIELDS_DONE
        else:
            message = messages.EMPLOYEE_BINDING_EMAIL_DONE

        self.render(
            template_name='refer/weixin/employee/employee_binding_tip.html',
            result=0,
            messages=message,
            nexturl=next_url,
            source=1)
        return


class BindedHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):

        binding_status, employee = yield self.employee_ps.get_employee_info(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        # unbinded users may not need to know this page
        if (self.employee_ps.convert_bind_status_from_thrift_to_fe(
            binding_status) !=
                fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS):
            self.write_error(404)

        else:
            self.render(
                template_name='refer/weixin/employee/employee_binding_tip.html',
                result=0,
                messages=messages.EMPLOYEE_BINDING_SUCCESS,
                nexturl=make_url(path.POSITION_LIST, self.params,
                                 recomlist=const.YES)
            )
