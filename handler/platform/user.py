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
import copy


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
                                    "map": "",
                                    "error_msg": "",
                                    "field_type": 10,
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
                                            "计算机/通信/电子/互联网",
                                            "1"
                                        ],
                                        [
                                            "会计/金融/银行/保险",
                                            "2"
                                        ],
                                        [
                                            "房地产/建筑业",
                                            "3"
                                        ],
                                        [
                                            "商业服务/教育/培训",
                                            "4"
                                        ],
                                        [
                                            "贸易/批发/零售/租赁业",
                                            "5"
                                        ],
                                        [
                                            "制药/医疗",
                                            "6"
                                        ],
                                        [
                                            "广告/媒体",
                                            "7"
                                        ],
                                        [
                                            "生产/加工/制造",
                                            "8"
                                        ],
                                        [
                                            "交通/运输/物流/仓储",
                                            "9"
                                        ],
                                        [
                                            "服务业",
                                            "10"
                                        ],
                                        [
                                            "文化/传媒/娱乐/体育",
                                            "11"
                                        ],
                                        [
                                            "能源/矿产/环保",
                                            "12"
                                        ],
                                        [
                                            "政府/非盈利机构/其他",
                                            "13"
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
                                    "field_type": 101,
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
                                    "field_description": "请填写城市名",
                                    "validate_re": "[\\s\\S]+"
                                },
                                {
                                    "map": "",
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
        data = ObjectDict(
            kind=0,  # // {0: success, 1: failure, 10: email}
            messages=['信息提交成功'],  # ['hello world', 'abjsldjf']
            button_text=msg.PREVIEW_PROFILE,
            button_link=self.make_url(path.PROFILE_VIEW,
                                      wechat_signature=self.get_argument('wechat_signature'),
                                      host=self.host,
                                      params=self.params),
            jump_link=self.make_url(path.PROFILE_VIEW,
                                    wechat_signature=self.get_argument('wechat_signature'),
                                    host=self.host,
                                    params=self.params)  # // 如果有会自动，没有就不自动跳转
        )

        self.render_page(template_name="system/user-info.html",
                         data=data)
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
        ret = copy.deepcopy(custom_cv_other_raw)

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

        if self._fans():
            position_list = yield self.get_fans_position_list()
            self.send_json_success(data={"positions": position_list})

        elif self._employee():
            position_list = yield self.get_employee_position_list()
            self.send_json_success(data={"positions": position_list})

        else:
            self.send_json_error("参数错误")

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

        position_list = yield self.position_ps.infra_get_position_personarecom(infra_params, company_id)
        return position_list

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

            position_list = yield self.position_ps.infra_get_position_employeerecom(infra_params, company_id)
        else:
            position_list = []

        return position_list
