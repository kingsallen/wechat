# coding=utf-8


from thrift.Thrift import TException
from tornado import gen

import conf.common as const
from handler.base import BaseHandler
from thrift_gen.gen.employee.struct.ttypes import BindingParams
from util.common.decorator import handle_response, authenticated
from util.common import ObjectDict


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

        # res = yield self.employee_ps.get_recommend_records(self.current_user.sysuser.id, page_no, page_size)
        # data = res.data
        res = ObjectDict({
            "status": 0,
            "message": "SUCCESS",
            "data": ObjectDict({
                "has_recommends": True,  # 是否有推荐记录
                "score": {
                    "link_viewed_count": 23, # 浏览人次 type=1
                    "interested_count": 10, # 求推荐人次 type=2
                    "applied_count": 10, # 投了简历人次 type=3
                },
                "recommends": [
                    ObjectDict({
                        "status": 0, # 求职的进度，含义，需要参考 das 的代码
                        "is_interested": '1', # 是否求推荐
                        "headimgurl": '',
                        "applier_name": 'towry',
                        "applier_rel": '汤亦亮', # 前端会显示为(汤亦亮的好友),表示 towry 是汤亦亮的好友
                        "view_number": 0, # 浏览次数
                        "position": 'position2', # 浏览的职位名称
                        "click_time": '2013-10-12', # 浏览时间
                        "recom_status": '0', # 0: 已推荐 1：未推荐
                    }),
                    ObjectDict({
                        "status": 1,
                        "is_interested": '0',
                        "headimgurl": '',
                        "applier_name": 'duolala',
                        "applier_rel": '',  # 前端会显示为(汤亦亮的好友),表示 towry 是汤亦亮的好友
                        "view_number": 4,
                        "position": 'position5',
                        "click_time": '2017-12-12',
                        "recom_status": '1',
                    }),
                    ObjectDict({
                        "status": 2,
                        "is_interested": '1',
                        "headimgurl": '',
                        "applier_name": '习大大',
                        "applier_rel": 'dodada',  # 前端会显示为(汤亦亮的好友),表示 towry 是汤亦亮的好友
                        "view_number": 12,
                        "position": 'position3',
                        "click_time": '2016-08-12',
                        "recom_status": '0',
                    }),
                ],
                page_no: 1, # 当前的页码
            })
        })

        if res.status == const.API_SUCCESS and res.data.recommends:
            self.logger.debug("recommends: %s" % res.data.recommends)
            for item in res.data.recommends:
                self.logger.debug("item: %s" % item)
                item['headimgurl'] = self.static_url(item.headimgurl or const.SYSUSER_HEADIMG),

        self.send_json_success(data=res.data)
