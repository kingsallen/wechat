# coding=utf-8

"""这个模块主要是给数据组 AI 项目收集数据使用的
"""

from tornado import gen

import conf.path as path
import conf.message as msg
import util.common.decorator as decorator
from handler.base import BaseHandler
from util.common import ObjectDict
from util.common.exception import MyException
from util.common.mq import data_userprofile_publisher
import conf.common as const
from util.tool.json_tool import json_dumps
from util.common.cipher import decode_id
import copy
import json


class UserSurveyConstantMixin(object):
    constant = ObjectDict()

    constant.job_grade = {
        1: "副总裁及以上",
        2: "总监",
        3: "经理",
        4: "主管",
        5: "职员",
        6: "应届生/学生"
    }

    constant.industry = {
        1: "计算机/互联网/通信/电子",
        2: "会计/金融/银行/保险",
        3: "贸易/消费/制造/营运",
        4: "制药/医疗",
        5: "生产/加工/制造",
        6: "广告/媒体",
        7: "房地产/建筑",
        8: "专业服务/教育/培训",
        9: "服务业",
        10: "物流/运输",
        11: "能源/原材料",
        12: "政府/非赢利机构/其他"
    }

    constant.salary = {
        1: "2K以下",
        2: "2k-4k",
        3: "4k-6k",
        4: "6k-8k",
        5: "8k-10k",
        6: "10k-15k",
        7: "15k-25k",
        8: "25k及以上"
    }

    constant.degree = {
        1: '初中及以下',
        2: '中专',
        3: '高中',
        4: '大专',
        5: '本科',
        6: '硕士',
        7: '博士',
        8: '博士以上',
        9: '其他'
    }

    @staticmethod
    def listify_dict(input_dict):
        return [[v, k] for k, v in input_dict.items()]


class UserSurveyHandler(BaseHandler):
    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """直接给数据组提供数据来源，以后拓展为可配置项，可以写进dict_constant中"""
        data = {
            "config":
                [
                    {
                        "fields":
                            [
                                {
                                    "map": "",
                                    "error_msg": "",
                                    "field_type": 10,
                                    "company_id": 0,
                                    "field_name": "degree",
                                    "required": 0,
                                    "id": 17,
                                    "priority": 17,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 3104,
                                    "field_value": [
                                        [
                                            "初中及以下",
                                            "1"
                                        ],
                                        [
                                            "中专",
                                            "2"
                                        ],
                                        [
                                            "高中",
                                            "3"
                                        ],
                                        [
                                            "大专",
                                            "4"
                                        ],
                                        [
                                            "本科",
                                            "5"
                                        ],
                                        [
                                            "硕士",
                                            "6"
                                        ],
                                        [
                                            "博士",
                                            "7"
                                        ],
                                        [
                                            "博士以上",
                                            "8"
                                        ],
                                        [
                                            "其他",
                                            "9"
                                        ]
                                    ],
                                    "field_title": "最高学历",
                                    "field_description": "请选择最高学历",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "",
                                    "error_msg": "从业年数最多只允许输入2位数字",
                                    "field_type": 0,
                                    "company_id": 0,
                                    "field_name": "workyears",
                                    "required": 0,
                                    "id": 32,
                                    "priority": 32,
                                    "parent_id": 0,
                                    "is_basic": 2,
                                    "constant_parent_code": 0,
                                    "field_value": [
                                        [
                                            ""
                                        ]
                                    ],
                                    "field_title": "从业年数",
                                    "field_description": "请填写年数",
                                    "validate_re": "^\\d{1,2}$"
                                },
                                {
                                    "map": "profile_basic.city_name",
                                    "error_msg": "",
                                    "field_type": 101,
                                    "company_id": 0,
                                    "field_name": "location",
                                    "required": 0,
                                    "id": 16,
                                    "priority": 16,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 0,
                                    "field_value": [
                                        [
                                            ""
                                        ]
                                    ],
                                    "field_title": "现居住地",
                                    "field_description": "请选择城市",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "",
                                    "error_msg": "最近工作的公司/品牌最多只允许输入100个字符",
                                    "field_type": 0,
                                    "company_id": 0,
                                    "field_name": "companyBrand",
                                    "required": 0,
                                    "id": 50,
                                    "priority": 50,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 0,
                                    "field_value": [
                                        [
                                            ""
                                        ]
                                    ],
                                    "field_title": "最近工作的公司/品牌",
                                    "field_description": "请填写公司名称",
                                    "validate_re": "[\\s\\S]{1,100}"
                                },
                                {
                                    "map": "",
                                    "error_msg": "最近工作职位最多只允许输入100个字符",
                                    "field_type": 0,
                                    "company_id": 0,
                                    "field_name": "current_position",
                                    "required": 0,
                                    "id": 0,
                                    "priority": 0,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 0,
                                    "field_value": [
                                        [
                                            ""
                                        ]
                                    ],
                                    "field_title": "当前/最近职位",
                                    "field_description": "请填写职位名称",
                                    "validate_re": "[\\s\\S]{1,100}"
                                }

                            ]
                    },
                    {
                        "fields":
                            [
                                {
                                    "map": "profile_intention.id&profile_intention_industry.industry_name",
                                    "error_msg": "",
                                    "field_type": 107,
                                    "company_id": 0,
                                    "field_name": "industry",
                                    "required": 0,
                                    "id": 48,
                                    "priority": 48,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 3124,
                                    "field_value": [
                                        [
                                            ""
                                        ]
                                    ],
                                    "field_title": "期望行业",
                                    "field_description": "请选择期望行业",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "profile_intention.worktype",
                                    "error_msg": "",
                                    "field_type": 10,
                                    "company_id": 0,
                                    "field_name": "worktype",
                                    "required": 0,
                                    "id": 0,
                                    "priority": 0,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 3105,
                                    "field_value": [
                                        [
                                            "没选择",
                                            "0"
                                        ],
                                        [
                                            "全职",
                                            "1"
                                        ],
                                        [
                                            "兼职",
                                            "2"
                                        ],
                                        [
                                            "实习",
                                            "3"
                                        ]
                                    ],
                                    "field_title": "工作类型",
                                    "field_description": "请选择工作类型",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "profile_intention.salary_code",
                                    "error_msg": "",
                                    "field_type": 10,
                                    "company_id": 0,
                                    "field_name": "salary_code",
                                    "required": 0,
                                    "id": 0,
                                    "priority": 0,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 3114,
                                    "field_value": [
                                        [
                                            "未填写",
                                            "0"
                                        ],
                                        [
                                            "2k以下",
                                            "1"
                                        ],
                                        [
                                            "2k-4k",
                                            "2"
                                        ],
                                        [
                                            "4k-6k",
                                            "3"
                                        ],
                                        [
                                            "6k-8k ",
                                            "4"
                                        ],
                                        [
                                            "8k-10k",
                                            "5"
                                        ],
                                        [
                                            "10k-15k",
                                            "6"
                                        ],
                                        [
                                            "15k-25k",
                                            "7"
                                        ],
                                        [
                                            "25k及以上",
                                            "8"
                                        ]
                                    ],
                                    "field_title": "期望月薪",
                                    "field_description": "请选择期望月薪",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "profile_intention.id&profile_intention_city.city_name",
                                    "error_msg": "",
                                    "field_type": 106,
                                    "company_id": 0,
                                    "field_name": "expectedlocation",
                                    "required": 0,
                                    "id": 37,
                                    "priority": 36,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 0,
                                    "field_value": [
                                        [
                                            ""
                                        ]
                                    ],
                                    "field_title": "期望工作城市",
                                    "field_description": "请选择城市",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "profile_intention.workstate",
                                    "error_msg": "",
                                    "field_type": 10,
                                    "company_id": 0,
                                    "field_name": "workstate",
                                    "required": 0,
                                    "id": 47,
                                    "priority": 47,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 3102,
                                    "field_value": [
                                        [
                                            "在职，看看新机会",
                                            "1"
                                        ],
                                        [
                                            "在职，急寻新工作",
                                            "2"
                                        ],
                                        [
                                            "在职，暂无跳槽打算",
                                            "3"
                                        ],
                                        [
                                            "离职，正在找工作",
                                            "4"
                                        ],
                                        [
                                            "应届毕业生",
                                            "5"
                                        ]
                                    ],
                                    "field_title": "工作状态",
                                    "field_description": "请选择工作状态",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "",
                                    "error_msg": "",
                                    "field_type": 10,
                                    "company_id": 0,
                                    "field_name": "icanstart",
                                    "required": 0,
                                    "id": 40,
                                    "priority": 40,
                                    "parent_id": 0,
                                    "is_basic": 0,
                                    "constant_parent_code": 3106,
                                    "field_value": [
                                        [
                                            "随时",
                                            "1"
                                        ],
                                        [
                                            "2周",
                                            "2"
                                        ],
                                        [
                                            "一个月",
                                            "3"
                                        ],
                                        [
                                            "一个月以上",
                                            "4"
                                        ]
                                    ],
                                    "field_title": "到岗时间",
                                    "field_description": "请选择到岗时间",
                                    "validate_re": "[\\s\\S]+"
                                }
                            ]
                    }
                ]
        }
        self.render_page('adjunct/user-survey.html', data=data)


class APIUserSurveyHandler(BaseHandler):
    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def post(self):
        """获取前端传过来的数据，POST json string格式"""

        model = self.json_args.model
        self.logger.debug("model_raw: %s" % model)

        # model = self.process_model_raw(model_raw)
        model.update(user_id=self.current_user.sysuser.id)
        self.logger.debug("model: %s" % model)
        # {'job_grade': '副总裁及以上', 'birth': '2018-05-10', 'salary': '2K以下', 'industry': '计算机/互联网/通信/电子', 'expected_position': '传达室', 'degree': '初中及以下', 'user_id': 5279773, 'city': '查实的'}

        self.logger.debug('pushed to rebbitmq')

        data_userprofile_publisher.publish_message(message=model)

        # 粉丝问卷调查入库
        yield self._save_model(model)
        self.send_json_success()
        return

    def process_model_raw(self, model_raw):
        model = model_raw
        for key in model:
            if key in self.constant:
                model[key] = getattr(self.constant, key).get(model[key])
        return model

    @gen.coroutine
    def _save_model(self, custom_cv):

        # --8<-- 初始化 --8<-----8<-----8<-----8<-----8<-----8<-----8<-----8<--
        custom_cv_tpls = yield self.profile_ps.get_custom_tpl_all()

        custom_cv_user_user = self.profile_ps.convert_customcv(custom_cv, custom_cv_tpls, target='user_user')
        custom_cv_profile_basic = self.profile_ps.convert_customcv(custom_cv, custom_cv_tpls, target='profile_basic')
        custom_cv_other_raw = self.profile_ps.convert_customcv(custom_cv, custom_cv_tpls, target='other')

        self.logger.debug("custom_cv_user_user: %s" % custom_cv_user_user)
        self.logger.debug("custom_cv_profile_basic: %s" % custom_cv_profile_basic)
        self.logger.debug("custom_cv_other_raw: %s" % custom_cv_other_raw)

        # --8<-- 更新 user_user --8<-----8<-----8<-----8<-----8<-----8<------
        if custom_cv_user_user:
            result = yield self.user_ps.update_user(
                self.current_user.sysuser.id,
                **custom_cv_user_user)

            self.logger.debug("update_user result: %s" % result)

        # --8<-- 检查profile --8<-----8<-----8<-----8<-----8<-----8<-----8<---
        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)
        if has_profile:
            profile_id = profile.get("profile", {}).get("id")
        else:
            # 还不存在 profile， 创建 profile
            # 进入自定义简历创建 profile 逻辑的话，来源必定是企业号（我要投递）
            result, data = yield self.profile_ps.create_profile(
                self.current_user.sysuser.id,
                source=const.PROFILE_SOURCE_PLATFORM_APPLY)

            # 创建 profile 成功
            if not result:
                raise RuntimeError('profile creation error')

            profile_id = data

            self._log_customs.update(new_profile=const.YES)

        # 创建完 profile 后再次获取 profile
        has_profile, profile = yield self.profile_ps.has_profile(
            self.current_user.sysuser.id)

        if custom_cv_profile_basic:
            # 已经有 profile，
            basic = profile.get("basic")

            result, data = yield self.profile_ps.get_profile_basic(profile_id=profile_id)

            has_no_basic = not result and data.status == 90010

            basic.update(custom_cv_profile_basic)
            self.logger.debug("updated basic: %s" % basic)

            if has_no_basic:
                basic.update({'profile_id': profile_id})
                yield self.profile_ps.create_profile_basic(
                    basic, profile_id, mode='c')
            else:
                yield self.profile_ps.update_profile_basic(profile_id, basic)

        # 更新多条 education, workexp, projectexp, language, awards,
        # 更新单条 intention, works
        yield self.profile_ps.update_profile_embedded_info_from_cv(
            profile_id, profile, custom_cv)

        # 更新 other
        if custom_cv_other_raw:
            yield self.update_profile_other(profile_id, custom_cv_other_raw)

    @gen.coroutine
    def update_profile_other(self, profile_id, custom_cv_other_raw):
        """智能地更新 profile_other 内容"""

        custom_cv_ready = self._preprocess_custom_cv(custom_cv_other_raw)

        other_string = json_dumps(custom_cv_ready)
        record = ObjectDict(other=other_string)

        yield self.application_ps.update_profile_other(record, profile_id)

    @staticmethod
    def _preprocess_custom_cv(custom_cv_other_raw):
        """对于纯 profile 字段的预处理
        可以在此加入公司自定义逻辑"""
        ret = json.dumps(custom_cv_other_raw)
        ret = json.loads(ret)

        # 前端 rocketmajor_value 保存应该入库的 rocketmajor 字段内容
        if ret.get('rocketmajor_value'):
            ret['rocketmajor'] = ret.get('rocketmajor_value')
            del ret['rocketmajor_value']

        # 确保保存正确的 schooljob 和 internship
        def _filter_elements_in(name):
            new_list = []
            for e in ret.get(name):
                if e.get('__status') and not e.get('__status') == 'x':
                    e.pop('__status', None)
                    until_now_key = name + 'end_until_now'
                    until_now = int(e.get(until_now_key, '0'))
                    if until_now:
                        e['end_date'] = None
                    new_list.append(e)
            return new_list

        if ret.get('internship'):
            ret['internship'] = _filter_elements_in('internship')

        if ret.get('schooljob'):
            ret['schooljob'] = _filter_elements_in('schooljob')

        return ret


class AIRecomHandler(BaseHandler):
    RECOM_AUDIENCE_COMMON = 1

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        recom_audience = self.RECOM_AUDIENCE_COMMON

        if self.params.recom_audience and self.params.recom_audience.isdigit():
            recom_audience = int(self.params.recom_audience)

        self.render_page('adjunct/job-recom-list.html',
                         data={'recomAudience': recom_audience})


class APIPositionRecomListHandler(BaseHandler):
    """
    AI推荐项目, 粉丝推荐职位/员工推荐职位接口,
    通过一个参数audience来区分粉丝和员工, 1表示粉丝 2表示员工
    """
    RECOM_AUDIENCE_COMMON = 1
    RECOM_AUDIENCE_EMPLOYEE = 2

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):

        if hasattr(self.params, "audience") and self.params.audience.isdigit():
            self.params.audience = int(self.params.audience)
        else:
            raise MyException("参数错误")

        social_res, school_res = yield self.application_ps.get_application_apply_status(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )

        if self._fans():
            position_list, total_count = yield self.get_fans_position_list()

        elif self._employee():
            position_list, total_count = yield self.get_employee_position_list()

        else:
            self.send_json_error("参数错误")
            return

        for pos in position_list:
            can_apply = False
            if pos.candidate_source:
                can_apply = school_res

            elif pos.candidate_source == 0:
                can_apply = social_res

            pos['can_apply'] = can_apply

        self.send_json_success(data={"positions": position_list, "total_count": total_count})

    def _fans(self):
        return self.params.audience == self.RECOM_AUDIENCE_COMMON

    def _employee(self):
        return self.params.audience == self.RECOM_AUDIENCE_EMPLOYEE

    @gen.coroutine
    def get_fans_position_list(self):
        """
        获取粉丝职位列表
        """
        company_id = self.current_user.company.id

        infra_params = ObjectDict({
            'pageNum': self.params.pageNo,
            'pageSize': self.params.pageSize,
            'userId': self.current_user.sysuser.id,
            "companyId": company_id,
            "type": 0  # hard code, 0表示粉丝
        })

        position_list, total_count = yield self.position_ps.infra_get_position_personarecom(infra_params, company_id)
        return position_list, total_count

    @gen.coroutine
    def get_employee_position_list(self):
        """
        获取员工推荐职位列表, 希望你能转发
        :return:
        """
        if int(self.params.pageNo) == 1:  # 不分页
            company_id = self.current_user.company.id
            infra_params = ObjectDict({
                "companyId": company_id,
                "recomPushId": int(self.params.recomPushId),
                "type": 1  # hard code, 1表示员工
            })

            position_list, total_count = yield self.position_ps.infra_get_position_employeerecom(infra_params,
                                                                                                 company_id)
        else:
            position_list = []
            total_count = 0

        return position_list, total_count


class APIPositionRecomListCloseHandler(BaseHandler):

    @decorator.handle_response
    @decorator.check_and_apply_profile
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        res = yield self.position_ps.get_recom_position_list_wx_tpl_receive(
            user_id=self.current_user.sysuser.id,
            wechat_id=self.current_user.wechat.id
        )
        data = res.get('data') or {}

        intention_id = None
        self.logger.debug('\n\n\ndebug_intentions_id:%s\n\n\n' % self.current_user)
        if self.current_user.profile and self.current_user.profile.intentions:
            intention_id = self.current_user.profile.intentions[0].get('id')

        data.update(dict(
            intention_id=intention_id
        ))
        self.write(res)

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def post(self):
        res = yield self.position_ps.not_receive_recom_position_wx_tpl(
            user_id=self.current_user.sysuser.id,
            wechat_id=self.current_user.wechat.id
        )
        self.write(res)


class PositionDetailPopupHandler(BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """
        候选人查看职位详情页面 获取该候选人是否关注公众号和简历完整度信息 然后前端根据结果给适当的引导弹窗
        弹窗1: 公众号二维码
        弹窗2：提示完善简历信息
        :return:
        """
        pid = self.params.position_id
        res = yield self.user_ps.get_popup_info(
            user_id=self.current_user.sysuser.id,
            company_id=self.current_user.company.id,
            position_id=pid
        )
        res_data = res.get('data')
        if not res_data:
            self.send_json_error(message='获取弹层信息失败')
            return

        res_crucial_info_switch = yield self.company_ps.get_crucial_info_state(self.current_user.company.id)
        switch = res_crucial_info_switch['data']

        data = dict(
            pv=res_data['current_position_count'],
            df_pv=res_data['position_view_count'],
            profile_completeness=res_data['profile_completeness'],
            switch=dict(
                df_pv_qrcode=res_data['position_wx_layer_qrcode'],
                df_pv_profile=res_data['position_wx_layer_profile'],
                recom_info_switch=switch
            )
        )
        self.send_json_success(data)


class PositionForwardFromEmpHandler(BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """
        候选人打开转发的职位链接，根据链接中参数判断最初转发该职位的人是否是员工
        决定前端是否显示“帮我内推”button
        :return:
        """
        pid = self.params.pid
        if not self.params.recom:
            self.send_json_success(data={
                "is_employee": 0,
                "employee_name": '',
                "employee_icon": '',
            })
            return
        if self.params.root_recom:
            # 人脉连连看页面目标用户打开的职位链接
            recom = decode_id(self.params.root_recom)
            psc = -1
        else:
            recom = decode_id(self.params.recom)
            psc = self.params.psc if self.params.psc else 0
        click_user_id = self.current_user.sysuser.id
        ret = yield self.user_ps.if_referral_position(
            self.current_user.company.id,
            recom, psc, pid, click_user_id)
        if not ret.status == const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return

        data = {
            "is_employee": ret.data['employee'],
            "employee_name": self.hideName(ret.data['user']['name']) if ret.data['employee'] else '',
            "employee_icon": ret.data['user']['avatar'] if ret.data['employee'] else '',
            "employee_id": ret.data['employee_id'] if ret.data.get("employee_id") else 0,
        }
        self.send_json_success(data)

    # IM优化 职位详情页浮层，在求职者查看员工姓名时，只显示第一个字，其他以*代替，开头为英文or其他字符的，显示1个字符
    def hideName(self,name):
        print("hideName(%s) type:%s len:%s" % ( name,type(name),len(name)))
        if len(name) == 0 :
            return name
        d = name.decode('utf8')
        str = d[0]
        loop = len(d) - 1
        while loop > 0 :
            str += u'*'
            loop = loop-1 ;
        return str.encode('utf8')

class ContactReferralInfoHandler(BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """
         联系内推页面获取员工姓名，头像，职位名
         判断该候选人是否已经点击过“帮我内推”并且确认提交，如果已提交过直接到确认提交后的一页
        :return:
        """
        pid = self.params.pid
        if self.params.root_recom:
            recom = decode_id(self.params.root_recom)
            psc = -1
        else:
            recom = decode_id(self.params.recom)
            psc = self.params.psc if self.params.psc else 0

        # 通知基础服务发送员工候选人聊天室消息末班
        self.chatting_ps.post_invite_message(self.current_user.company.id,
                                             self.params.employee_id,
                                             pid,
                                             self.current_user.sysuser.id,
                                             3,
                                             psc)

        if_seek_check_ret = yield self.user_ps.if_ever_seek_recommend(
            recom, psc, pid,
            self.current_user.company.id,
            self.current_user.sysuser.id
        )
        if not if_seek_check_ret.status == const.API_SUCCESS:
            self.write_error(500, message=if_seek_check_ret.message)
            return

        if if_seek_check_ret.data.get('referral_id'):
            self.render_page(template_name='employee/result-with-jobs.html',
                             data=dict())
            return

        ret = yield self.user_ps.if_referral_position(
            self.current_user.company.id,
            recom, psc, pid, self.current_user.sysuser.id)
        if not ret.status == const.API_SUCCESS:
            self.write_error(500, message=ret.message)
            return

        recom_user_id = ret.data['user']['uid']

        ret_info = yield self.employee_ps.referral_contact_push(recom_user_id, pid)
        if not ret_info.status == const.API_SUCCESS:
            self.write_error(500, message=ret_info.message)
            return

        self.render_page(
            template_name='employee/connect-referral.html',
            data={
              "employee_icon": ret_info.data['employee_icon'],
              "employee_name": ret_info.data['employee_name'],
              "position_name": ret_info.data['position_name'],
              "pid": pid,
            }
        )


class ReferralRelatedPositionHandler(BaseHandler):

    @decorator.handle_response
    @decorator.authenticated
    @gen.coroutine
    def get(self):
        """
        联系内推完成后 给出该公司三个相关职位
        :return:
        """

        ret = yield self.user_ps.referral_related_positions(
            self.current_user.sysuser.id,
            self.current_user.company.id
        )
        if not ret.status == const.API_SUCCESS:
            self.send_json_error(message=ret.message)
            return

        data = list()
        for item in ret.data:
            item_return = item
            if item.get('experience'):
                if item.get('experience_above'):
                    item_return.update({'experience': str(item.get('experience')) + '年及以上'})
                else:
                    item_return.update({'experience': str(item.get('experience')) + '年'})

            if item.get('degree') and item.get('degree_above'):
                item_return.update({'degree': const.POSITION_DEGREE.get(str(item.get('degree'))) + '及以上'})
            else:
                item_return.update({'degree': const.POSITION_DEGREE.get(str(item.get('degree')))})

            if item.get('hb_status'):
                item_return.update({'has_reward': 1})

            data.append(item_return)

        self.send_json_success(data={
            "list": data
        })
