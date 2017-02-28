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
            reward_configs = result.rewardCofnigs
            total = result.total
        else:
            # 使用初始化数据
            pass

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

        self.send_json_success(data={
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
    def get(self):
        data = {
            'type':            'email',
            'binding_message': 'binding message ...',
            'binding_status':  1,
            'send_hour':       2,
            'headimg':         'http://o8g4x4uja.bkt.clouddn.com/0.jpeg',
            'employeeid':      23,
            'name':            'name',
            'mobile':          '15000234929',
            'conf':            {
                'custom_name':   'custom',
                'custom_hint':   'custom hint',
                'custom_value':  'user input value for custom',
                ''
                'email_suffixs': [
                    'qq.com',
                    'foxmail.com',
                ],
                'email_name':    'tovvry',
                'email_suffix':  'qq.com',

                # // 最多两个问题
                'questions':     [
                    {'q': "你的姓名是什么", 'a': 'b', id: 1},
                    {'q': "你的弟弟的姓名是什么", 'a': 'a', id: 2},
                ],
                # // null, question, or email
                'switch':        'email',
            }
        }

        self.send_json_success(data=data)


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
        # res = ObjectDict({
        #     "status": 0,
        #     "message": "SUCCESS",
        #     "data": ObjectDict({
        #         "has_recommends": True,  # 是否有推荐记录
        #         "score": {
        #             "link_viewed_count": 23, # 浏览人次 type=1
        #             "interested_count": 10, # 求推荐人次 type=2
        #             "applied_count": 10, # 投了简历人次 type=3
        #         },
        #         "recommends": [
        #             ObjectDict({
        #                 "status": 0, # 求职的进度，含义，需要参考 das 的代码
        #                 "is_interested": '1', # 是否求推荐
        #                 "headimgurl": '',
        #                 "applier_name": 'towry',
        #                 "applier_rel": '汤亦亮', # 前端会显示为(汤亦亮的好友),表示 towry 是汤亦亮的好友
        #                 "view_number": 0, # 浏览次数
        #                 "position": 'position2', # 浏览的职位名称
        #                 "click_time": '2013-10-12', # 浏览时间
        #                 "recom_status": '0', # 0: 已推荐 1：未推荐
        #             }),
        #             ObjectDict({
        #                 "status": 1,
        #                 "is_interested": '0',
        #                 "headimgurl": '',
        #                 "applier_name": 'duolala',
        #                 "applier_rel": '',  # 前端会显示为(汤亦亮的好友),表示 towry 是汤亦亮的好友
        #                 "view_number": 4,
        #                 "position": 'position5',
        #                 "click_time": '2017-12-12',
        #                 "recom_status": '1',
        #             }),
        #             ObjectDict({
        #                 "status": 2,
        #                 "is_interested": '1',
        #                 "headimgurl": '',
        #                 "applier_name": '习大大',
        #                 "applier_rel": 'dodada',  # 前端会显示为(汤亦亮的好友),表示 towry 是汤亦亮的好友
        #                 "view_number": 12,
        #                 "position": 'position3',
        #                 "click_time": '2016-08-12',
        #                 "recom_status": '0',
        #             }),
        #         ],
        #     })
        # })

        self.logger.debug("get_recommend_records: %s" % res)

        if res:
            for item in res.recommends:
                item['headimgurl'] = self.static_url(item.headimgurl or const.SYSUSER_HEADIMG),

        self.send_json_success(data=res)
