# coding=utf-8

import json

from tornado import gen
import time
import conf.common as const
import conf.fe as fe
import conf.message as msg
import conf.path as path
from service.page.base import PageService
from setting import settings
from thrift_gen.gen.employee.struct.ttypes import BindingParams, BindStatus
from util.common import ObjectDict
from util.tool.dict_tool import sub_dict
from util.tool.re_checker import revalidator
from util.tool.url_tool import make_static_url, make_url
from util.tool.str_tool import gen_salary, gen_experience_v2
from util.wechat.core import get_temporary_qrcode
from util.common.mq import unread_praise_publisher
from util.common.decorator import log_time


class EmployeePageService(PageService):
    FE_BIND_TYPE_CUSTOM = 'custom'
    FE_BIND_TYPE_EMAIL = 'email'
    FE_BIND_TYPE_QUESTION = 'question'

    BIND_AUTH_MODE = ObjectDict({
        FE_BIND_TYPE_EMAIL: 0,
        FE_BIND_TYPE_CUSTOM: 1,
        FE_BIND_TYPE_QUESTION: 2
    })

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_valid_employee_record_by_activation_code(self, code):
        """通过新微信 DAO 来判断 activation code 对应的员工是否已经成功绑定
        用于email员工绑定点击链接后"""
        record = yield self.user_employee_ds.get_employee({
            'activation_code': code,
            'activation': const.OLD_YES,
            'disable': const.OLD_YES,
            'status': const.OLD_YES
        })
        return record

    @gen.coroutine
    def get_employee_info(self, user_id, company_id):
        """获取员工信息"""
        employee_response = yield self.thrift_employee_ds.get_employee(
            user_id, company_id)
        return employee_response.bindStatus, employee_response.employee

    @gen.coroutine
    def get_employee_info_by_user_id(self, user_id):
        """通过user_id获取员工信息"""
        res = yield self.infra_employee_ds.get_employee_by_user_id(user_id)
        if res.status == const.API_SUCCESS:
            data = ObjectDict({
                "employee_id": res.data.id,
                "wechat_signature": res.data.signature,
                "company_id": res.data.company_id
            })
        else:
            data = ObjectDict()
        return data

    @staticmethod
    def convert_bind_status_from_thrift_to_fe(thrift_bind_status):
        """convert bind status value to FE format"""
        fe_bind_status = fe.FE_EMPLOYEE_BIND_STATUS_DEFAULT_INVALID

        if thrift_bind_status == BindStatus.BINDED:
            fe_bind_status = fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS
        elif thrift_bind_status == BindStatus.UNBIND:
            fe_bind_status = fe.FE_EMPLOYEE_BIND_STATUS_UNBINDED
        elif thrift_bind_status == BindStatus.PENDING:
            fe_bind_status = fe.FE_EMPLOYEE_BIND_STATUS_PENDING
        else:
            pass
            # assert False  # should not be here

        return fe_bind_status

    @gen.coroutine
    def get_employee_bind_status(self, user_id, company_id):
        """获取员工绑定状态"""
        bind_status, _ = yield self.get_employee_info(user_id, company_id)
        return bind_status

    @gen.coroutine
    def make_binding_render_data(self, current_user, mate_num, reward, conf, custom_supply_info, custom_supply_field,
                                 auth_tips_info, is_valid_email=False, in_wechat=None, locale=None):
        """构建员工绑定页面的渲染数据
        :returns:
        {
          'type':            'email',
          'custom_title':    'custom title',
          'binding_tips_title': '认证须知'
          'binding_message': 'binding message ...',
          'binding_status':  1,
          'send_hour':       24,
          'headimg':         'http://o8g4x4uja.bkt.clouddn.com/0.jpeg',
          'employeeid':      23,
          'name':            'name',
          'mobile':          '15000234929',
          'conf':            {
            'custom_name':   'custom',
            'custom_hint':   'custom hint',
            'custom_value':  'user input value for custom',
            'email_suffixs': ['qq.com', 'foxmail.com'],
            'email_name':    'tovvry',
            'email_suffix':  'qq.com',
            'questions':     [ {'q': "你的姓名是什么", 'a':''}, {'q': "你的弟弟的姓名是什么", 'a': ''} ],
            # // null, question, or email
            'switch':        'email',
          },
          'custom_field':
            [
              {
                "id":1,
                "name":"部门",
                "ename": "department",
                "system_field": 1,  # 1部门，2职位，3城市，0非系统字段
                "option_type":0,  # 选项类型  0:下拉选项, 1:文本
                "values":[
                  {
                    "id":1,
                    "value":"test"
                    },
                 ]
              "enable":0, # 是否停用 0:不停用(有效)， 1:停用(无效)
              "required":1,	# 是否必填 0:不必填，1必填
            }
          ]
          'custom_info':
            [
              {"custom_field.id":
               "custom_field.values.id or ''"
              }
            ]
        """

        data = ObjectDict()
        # 员工认证自定义文案
        data.binding_message = auth_tips_info.description_ename if locale.code == const.LOCALE_ENGLISH else auth_tips_info.description
        data.binding_tips_title = auth_tips_info.tips_title_ename if locale.code == const.LOCALE_ENGLISH else auth_tips_info.tips_title
        data.custom_title = auth_tips_info.title_ename or const.PAGE_EN_VERIFICATION if locale.code == const.LOCALE_ENGLISH else auth_tips_info.title or const.PAGE_VERIFICATION

        data.wechat = ObjectDict()
        data.name = current_user.sysuser.name
        data.headimg = current_user.sysuser.headimg
        data.mobile = current_user.sysuser.mobile or ''
        data.send_hour = 24  # fixed 24 小时
        data.is_valid_email = is_valid_email
        data.conf = ObjectDict()
        data.binding_success_message = conf.bindSuccessMessage or ''

        # todo 公众号信息，已有接口，这个其实是重复的代码
        data.wechat.subscribed = True if not in_wechat or current_user.wxuser.is_subscribe or current_user.wechat.type == 0 else False
        data.wechat.qrcode = yield get_temporary_qrcode(
            wechat=current_user.wechat,
            scene_id=int('11110000000000000000000000000000', base=2) + int(const.QRCODE_BIND)
        )
        data.wechat.name = current_user.wechat.name

        data.mate_num = mate_num
        data.conf.reward = reward
        # 国际化补填信息的名称
        if locale.code == const.LOCALE_ENGLISH:
            for f in custom_supply_field:
                if f.get("ename"):
                    f['name'] = f.get("ename")

        data.custom_supply_field = custom_supply_field
        data.custom_supply_info = custom_supply_info

        bind_status, employee = yield self.get_employee_info(
            user_id=current_user.sysuser.id, company_id=current_user.company.id)

        # 当前是绑定状态
        if bind_status == BindStatus.BINDED:
            data.binding_status = fe.FE_EMPLOYEE_BIND_STATUS_SUCCESS
            data.employeeid = employee.id
            data.name = employee.cname

        # 当前是 pending 状态
        elif bind_status == BindStatus.PENDING:
            data.name = employee.cname
            data.mobile = employee.mobile
            data.binding_status = fe.FE_EMPLOYEE_BIND_STATUS_PENDING

        # 当前是未绑定状态
        else:
            # 否则，调用基础服务判断当前用户的认证状态：没有认证还是 pending 中
            data.employeeid = const.NO

            if bind_status == const.EMPLOYEE_BIND_STATUS_UNBINDING:
                data.binding_status = fe.FE_EMPLOYEE_BIND_STATUS_UNBINDED

            elif bind_status == const.EMPLOYEE_BIND_STATUS_EMAIL_PENDING:
                data.binding_status = fe.FE_EMPLOYEE_BIND_STATUS_PENDING
            else:
                data.binding_status = fe.FE_EMPLOYEE_BIND_STATUS_DEFAULT_INVALID

        if conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.DISABLE:
            data.type = 'disabled'
            return data

        def _make_custom_conf():
            data.conf.custom_hint = conf.customHint
            data.conf.custom_name = conf.custom
            if bind_status == const.EMPLOYEE_BIND_STATUS_BINDED:
                data.conf.custom_value = employee.customField
            else:
                data.conf.custom_value = ''

        def _make_questions_conf():
            if bind_status == const.EMPLOYEE_BIND_STATUS_BINDED:
                data.conf.questions = [ObjectDict(e) for e in conf.questions]
            else:
                data.conf.questions = [sub_dict(e, 'q') for e in conf.questions]

        # 已经绑定的员工，根据 employee.authMethod 来渲染
        if bind_status == BindStatus.BINDED:
            data.mobile = employee.mobile or ''
            if employee.authMethod == const.USER_EMPLOYEE_AUTH_METHOD.EMAIL:
                data.type = self.FE_BIND_TYPE_EMAIL
                data.name = employee.cname

                # 初始化 email_name, email_suffix 为空字符串
                # 随后根据员工的 email 填写数据
                data.conf.email_name = ''
                data.conf.email_suffix = ''
                if isinstance(employee.email, str) and '@' in employee.email:
                    data.conf.email_name = employee.email.split('@')[0]
                    data.conf.email_suffix = employee.email.split('@')[1]
            elif employee.authMethod == const.USER_EMPLOYEE_AUTH_METHOD.CUSTOM:
                data.type = self.FE_BIND_TYPE_CUSTOM
                _make_custom_conf()
            elif employee.authMethod == const.USER_EMPLOYEE_AUTH_METHOD.QUESTION:
                data.type = self.FE_BIND_TYPE_QUESTION
                _make_questions_conf()
            else:
                assert False  # should not be here

        # 未绑定的员工， 根据 conf.authMode 来渲染
        else:

            if conf.authMode in [const.EMPLOYEE_BIND_AUTH_MODE.EMAIL,
                                 const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_CUSTOM,
                                 const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_QUESTION]:
                data.type = self.FE_BIND_TYPE_EMAIL
                data.conf.email_suffixs = conf.emailSuffix
                if bind_status in [const.EMPLOYEE_BIND_STATUS_BINDED,
                                   const.EMPLOYEE_BIND_STATUS_EMAIL_PENDING]:
                    data.conf.email_name = ''
                    data.conf.email_suffix = ''
                    self.logger.debug(employee.email)
                    if isinstance(employee.email,
                                  str) and '@' in employee.email:
                        data.conf.email_name = employee.email.split('@')[0]
                        data.conf.email_suffix = employee.email.split('@')[1]
                else:
                    data.conf.email_name = ''
                    data.conf.email_suffix = data.conf.email_suffixs[0] if len(
                        data.conf.email_suffixs) else ''

                if conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_CUSTOM:
                    data.conf.switch = self.FE_BIND_TYPE_CUSTOM
                    _make_custom_conf()

                if conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_QUESTION:
                    data.conf.switch = self.FE_BIND_TYPE_QUESTION
                    _make_questions_conf()

            elif conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.CUSTOM:
                data.type = self.FE_BIND_TYPE_CUSTOM
                _make_custom_conf()

            elif conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.QUESTION:
                data.type = self.FE_BIND_TYPE_QUESTION
                _make_questions_conf()

            else:
                raise ValueError('invalid authMode')

        return data

    def make_bind_params(self, user_id, company_id, json_args, params):
        """
        构建员工绑定的参数集合
        :param user_id:
        :param company_id:
        :param json_args:
        :param params
        :return:
        """
        type = json_args.type
        source = int(params.source) if params.source and params.source.isdigit() else 0

        needed_keys = ['type', 'name', 'mobile', 'custom_supply_info']

        if type == self.FE_BIND_TYPE_CUSTOM:
            needed_keys.append('custom_value')
        elif type == self.FE_BIND_TYPE_EMAIL:
            needed_keys.append('email_name')
            needed_keys.append('email_suffix')
        elif type == self.FE_BIND_TYPE_QUESTION:
            needed_keys.append('answers')

        param_dict = sub_dict(json_args, needed_keys)

        if type == self.FE_BIND_TYPE_EMAIL:
            passed = revalidator.check_email_local(param_dict.email_name)
            if not passed:
                return False, msg.EMAIL_FMT_FAILURE

            param_dict.email = '%s@%s' % (param_dict.email_name, param_dict.email_suffix)
        if type == self.FE_BIND_TYPE_QUESTION:
            param_dict.answer1 = param_dict.answers[0]
            if len(param_dict.answers) > 1:
                param_dict.answer2 = param_dict.answers[1]
            else:
                param_dict.answer2 = ''

        # 将key的类型转为int, value转为str
        custom_supply_info = dict()
        if param_dict.custom_supply_info:
            for k, v in param_dict.custom_supply_info.items():
                custom_supply_info.update({int(k): str(v)})

        binding_params = BindingParams(
            type=self.BIND_AUTH_MODE[param_dict.type],
            userId=user_id,
            companyId=company_id,
            email=param_dict.email,
            mobile=str(param_dict.mobile),
            customField=param_dict.custom_value.strip() if param_dict.custom_value else param_dict.custom_value,
            name=param_dict.name.strip() if param_dict.name else param_dict.name,
            answer1=param_dict.answer1,
            answer2=param_dict.answer2,
            source=source,
            customFieldValues=custom_supply_info
        )

        return True, binding_params

    @gen.coroutine
    def get_employee_conf(self, company_id):
        """获取员工绑定配置"""
        ret = yield self.thrift_employee_ds.get_employee_verification_conf(
            company_id)
        return ret

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id, locale, page_number=1, page_size=10):
        """获取员工积分信息"""

        reason_txt_fmt_map = {
            const.RECRUIT_STATUS_RECOMCLICK_ID: "awards_reason_saw_profile",
            const.RECRUIT_STATUS_APPLY_ID: "awards_reason_aplied",
            const.RECRUIT_STATUS_CVPASSED_ID: "awards_reason_review_passed",
            const.RECRUIT_STATUS_OFFERED_ID: "awards_reason_passed_interview",
            const.RECRUIT_STATUS_FULL_RECOM_INFO_ID: "awards_reason_fullfil_info",
            const.RECRUIT_STATUS_HIRED_ID: "awards_reason_on_board",
        }
        reason_no_format = {
            const.RECRUIT_STATUS_VERIFICATION: "完成员工认证",
            const.RECRUIT_STATUS_UPLOAD_RESUME: "员工上传人才简历"
        }

        res_award_rules = []
        res_rewards = []

        rewards_thrift_res = yield self.thrift_employee_ds.get_employee_rewards(
            employee_id, company_id, page_number, page_size)

        rewards = rewards_thrift_res.rewards
        reward_configs = rewards_thrift_res.rewardConfigs
        total = rewards_thrift_res.total

        # 构建输出数据格式
        if reward_configs:
            for rc in reward_configs:
                e = ObjectDict()
                e.name = locale.translate(rc.statusName)
                e.point = rc.points
                res_award_rules.append(e)

        if rewards:
            for reward_vo in rewards:
                e = ObjectDict()

                # 根据申请进度由系统自动追加的积分
                if reward_vo.type in reason_txt_fmt_map and reward_vo.berecomName:
                    e.reason = locale.translate(reason_txt_fmt_map[reward_vo.type]).format(reward_vo.berecomName)
                elif reward_vo.type in reason_no_format:
                    e.reason = locale.translate(reason_no_format[reward_vo.type])
                # HR 手动增减积分添加的原因
                elif reward_vo.type == 0:
                    e.reason = reward_vo.reason
                else:
                    e.reason = ""
                e.title = reward_vo.positionName
                e.point = reward_vo.points
                e.create_time = reward_vo.updateTime
                res_rewards.append(e)

        return ObjectDict({
            'rewards': res_rewards,
            'award_rules': res_award_rules,
            'point_total': total
        })

    @gen.coroutine
    def get_bind_rewards(self, company_id):
        """获取积分配置"""
        result, data = yield self.infra_employee_ds.get_bind_reward(company_id)
        return data

    @gen.coroutine
    def get_bind_reward(self, company_id, type=None):
        """获取指定规则的积分配置, 如果未指定规则，则获取该公司是否有带积分奖励的积分规则"""
        result, data = yield self.infra_employee_ds.get_bind_reward(company_id)
        reward = 0
        if type:
            for r in data:
                if r.get("statusName") == type:
                    reward = r.get("points")
        else:
            for r in data:
                if r.get("points"):
                    return True
        return reward

    @gen.coroutine
    def get_employee_custom_info(self, current_user):
        """获取员工补填信息"""
        params = {
            "user_id": current_user.sysuser.id,
            "company_id": current_user.company.id
        }
        result = yield self.infra_employee_ds.infra_get_employee_custom_info(params)
        return result.data or ObjectDict()

    @gen.coroutine
    def get_employee_custom_field(self, current_user):
        """获取补填字段配置数据"""
        params = {
            "company_id": current_user.company.id
        }
        result = yield self.infra_employee_ds.infra_get_employee_custom_field(params)
        return result.data or []

    @gen.coroutine
    def get_employee_supply_info_by_custom_field(self, cname, custom_field, company_id):
        """获取补填字段配置数据"""
        params = {
            "cname": cname,
            "custom_field": custom_field,
            "company_id": company_id
        }
        result = yield self.infra_employee_ds.infra_get_employee_supply_info_by_custom_field(params)
        return result.data or ObjectDict()

    @gen.coroutine
    def get_employee_auth_tips_info(self, current_user):
        """获取认证自定义显示数据"""
        params = {
            "company_id": current_user.company.id
        }
        result = yield self.infra_employee_ds.infra_get_employee_auth_tips_info(params)
        return result.data or ObjectDict()

    @gen.coroutine
    def get_bind_email_is_valid(self, current_user):
        """获取认证邮件是否有效"""
        params = {
            "user_id": current_user.sysuser.id,
            "company_id": current_user.company.id
        }
        result = yield self.infra_employee_ds.infra_get_bind_email_is_valid(params)
        return result.data

    @gen.coroutine
    def resend_bind_email(self, current_user):
        """重新发送认证邮件"""
        params = {
            "user_id": current_user.sysuser.id,
            "company_id": current_user.company.id
        }
        result = yield self.infra_employee_ds.infra_resend_bind_email(params)
        return result

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):
        """员工解绑"""
        ret = yield self.thrift_employee_ds.unbind(
            employee_id, company_id, user_id)
        return ret.success, ret.message

    @gen.coroutine
    def bind(self, binding_params):
        """员工绑定"""
        ret = yield self.thrift_employee_ds.bind(binding_params)
        return ret.success, ret.message

    @gen.coroutine
    def activate_email(self, activation_code, bind_email_source):
        """通过邮箱激活员工"""
        ret = yield self.thrift_employee_ds.activate_email(activation_code, int(bind_email_source))
        return ret.success, ret.message, ret.employeeId

    @gen.coroutine
    def get_award_ladder_info(self, employee_id, company_id, type, page_from, page_size):
        """获取员工积分榜数据"""
        ret = yield self.thrift_employee_ds.get_award_ranking(
            employee_id, company_id, type, page_from, page_size)

        def gen_make_element(employee_award_list):
            for e in employee_award_list:
                yield ObjectDict({
                    'username': e.name,
                    'id': e.employeeId,
                    'point': e.awardTotal,
                    'icon': make_static_url(e.headimgurl),
                    'level': e.ranking,
                    'praise': e.praise,
                    'praised': e.praised
                })

        return list(gen_make_element(ret.data))

    @gen.coroutine
    def get_total_row_ladder_info(self, employee_id, company_id, type):
        """获取员工积分榜数据总数"""
        ret = yield self.thrift_employee_ds.get_award_ranking(
            employee_id, company_id, type)
        return ret.totalRow

    @gen.coroutine
    def vote_prasie(self, employee_id, praise_employee_id):
        """员工点赞"""
        result, _ = yield self.infra_employee_ds.vote_prasie(employee_id, praise_employee_id)
        return result

    @gen.coroutine
    def cancel_prasie(self, employee_id, praise_employee_id):
        """员工取消点赞"""
        result, _ = yield self.infra_employee_ds.cancel_prasie(employee_id, praise_employee_id)
        return result

    @gen.coroutine
    def get_referral_policy(self, company_id):
        """获取公司内推政策"""
        result, data = yield self.infra_employee_ds.get_referral_policy(company_id)
        return result, data

    @gen.coroutine
    def get_mate_num(self, company_id):
        """获取已验证员工数"""
        result, data = yield self.infra_employee_ds.get_mate_num(company_id)
        return data if result else 0

    @gen.coroutine
    def get_unread_praise(self, employee_id):
        """获取未读的赞的数量"""
        result, data = yield self.infra_employee_ds.get_unread_praise(employee_id)
        return data if result else 0

    @gen.coroutine
    def reset_unread_praise(self, employee_id):
        """阅读后，将未读的赞的数量清空"""
        data = ObjectDict({
            "employee_id": employee_id,
            "view_time": int(time.time() * 1000)
        })
        yield unread_praise_publisher.publish_message(message=data,
                                                      routing_key="employee_view_leader_board_routing_key")

    @gen.coroutine
    def get_last_rank_info(self, employee_id, type):
        """获取该公司积分榜单最后一名员工的榜单信息"""
        result, data = yield self.infra_employee_ds.get_last_rank_info(employee_id, type)
        return data

    @gen.coroutine
    def get_current_user_rank_info(self, employee_id, type):
        """获取当前用户榜单信息"""
        result, data = yield self.infra_employee_ds.get_current_user_rank_info(employee_id, type)
        return data

    @gen.coroutine
    def get_award_ladder_type(self, company_id):
        """获取榜单类型"""
        result, data = yield self.infra_employee_ds.get_award_ladder_type(company_id)
        if result:
            ladder_type = data.get("type")
        else:
            ladder_type = 2
        return ladder_type

    @gen.coroutine
    def create_interest_policy_count(self, params):
        """对公司内推政策感兴趣"""
        yield self.infra_employee_ds.create_interest_policy_count(params)

    @gen.coroutine
    def get_recommend_records(self, user_id, req_type, page_no, page_size):
        """
        推荐历史记录
        :param user_id:
        :param req_type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.thrift_useraccounts_ds.get_recommend_records(
            int(user_id), int(req_type), int(page_no), int(page_size))

        score = ObjectDict()
        if ret.score:
            score = ObjectDict({
                "link_viewed_count": ret.score.link_viewed_count,
                "interested_count": ret.score.interested_count,
                "applied_count": ret.score.applied_count
            })
        recommends = list()
        if ret.recommends:
            for e in ret.recommends:
                recom = ObjectDict({
                    "status": e.status,
                    "headimgurl": make_static_url(
                        e.headimgurl or const.SYSUSER_HEADIMG),
                    "is_interested": e.is_interested,
                    "applier_name": e.applier_name,
                    "applier_rel": e.applier_rel,
                    "view_number": e.view_number,
                    "position": e.position,
                    "click_time": e.click_time,
                    "recom_status": e.recom_status,
                    "id": e.id
                })
                recommends.append(recom)

        res = ObjectDict({
            "has_recommends": ret.hasRecommends if ret.hasRecommends else False,
            "score": score,
            "recommends": recommends
        })

        raise gen.Return(res)

    @gen.coroutine
    def get_employee_custom_fields(self, current_user, locale):
        """
        根据公司 id 返回员工认证自定义字段配置 -> list
        并按照 forder 字段排序返回
        将数据整理为前端需要的json格式
        """
        res = yield self.infra_employee_ds.infra_get_employee_custom_field({"company_id": current_user.company.id})
        selects_from_ds = res.data or []
        selects_list = list()

        for s in selects_from_ds:
            input_type = const.FRONT_TYPE_FIELD_TEXT if s.get("option_type") == 1 else const.FRONT_TYPE_FIELD_SELCET_POPUP
            if s.get("values"):
                field_value = [[v.get("name"), v.get("id")] for v in s.get("values")]
            else:
                field_value = []
            selects = ObjectDict({
                'field_title': s.get("ename") if locale.code == const.LOCALE_ENGLISH else s.get("name"),
                'field_type': input_type,
                'field_name': s.get("id"),
                'required': 0 if s.get("required") == 1 else 1,  # 0为必须
                'field_value': field_value,
                "validate_error": ""  # 字段不符合验证时的提示信息
            })
            selects_list.append(selects)
        return selects_list

    @gen.coroutine
    def update_employee_custom_fields(self, employee_id, custom_fields_json):
        yield self.thrift_employee_ds.set_employee_custom_info(
            employee_id, custom_fields_json)

    @gen.coroutine
    def update_employee_custom_supply_info(self, employee_id, company_id, custom_fields_json):
        params = ObjectDict({
            "companyId": company_id,
            "userEmployeeId": employee_id,
            "customFieldValues": custom_fields_json
        })
        res = yield self.infra_employee_ds.infra_update_employee_custom_supply_info(
            params)
        return res

    @gen.coroutine
    def submit_employee_subscribe_preference(self, employee_id, preference):
        """提交员工订阅偏好的信息"""
        params = ObjectDict({
            "employee_id": employee_id,
            "preference": preference
        })
        res = yield self.infra_employee_ds.infra_submit_employee_subscribe_preference(
            params)
        return res

    @gen.coroutine
    def update_employee_custom_fields_for_email_pending(
        self, user_id, company_id, custom_fields_json):
        yield self.thrift_employee_ds.set_employee_custom_info_email_pending(
            user_id, company_id, custom_fields_json)

    @gen.coroutine
    def get_employee_survey_info(self, user):
        """
        获取员工AI调查问卷填写的信息
        :param employee:
        :return:
        department: 1,
          job_grade: 2,
          degree: 1,
          city: "上海",
          city_code: 112,
          position: "前端开发"
        """
        result, data = yield self.infra_user_ds.get_employee_survey_info(user.sysuser.id, user.employee.id)
        if result:
            city_code = data["city_code"]
            city_name = yield self.infra_dict_ds.get_city_name_by(city_code)
            employee_survey_info = {
                "position": data["position"],
                "department": data["team_id"],
                "job_grade": data["job_grade"],
                "city": city_name,
                "city_code": data["city_code"],
                "degree": data["degree"]
            }
        else:
            employee_survey_info = {}
        return employee_survey_info

    @gen.coroutine
    def post_employee_survey_info(self, employee, survey):
        """
        提交员工问卷调查, 一律使用POST, 不区分新增/更新
        :param employee:
        :param survey:
        :return:
        """
        res = yield self.infra_user_ds.post_employee_survey_info(employee.id, survey)
        return res

    @gen.coroutine
    def get_employee_company_teams(self, company_id):
        """
        获取员工所在公司的所有团队
        :param employee:
        :return:
        """
        fields = ["id", "name"]
        teams = yield self.hr_team_ds.get_team_list(
            conds={'company_id': company_id, 'is_show': 1, 'disable': 0}, fields=fields)
        return teams

    @gen.coroutine
    def is_valid_employee(self, user_id, company_id):
        is_employee = yield self.infra_user_ds.is_valid_employee(user_id, company_id)
        return is_employee

    @gen.coroutine
    def update_recommend(self, employee_id, name, mobile, recom_reason, pid, type, relationship, recom_reason_text):
        params = ObjectDict({
            "name": name,
            "mobile": mobile,
            "referral_reasons": recom_reason,
            "position": pid,
            "referral_type": type,
            "relationship": relationship,
            "recom_reason_text": recom_reason_text
        })
        res = yield self.infra_user_ds.update_recommend(params, employee_id)
        return res

    @gen.coroutine
    def upload_recom_profile(self, file_name, file_data, employee_id):
        res = yield self.infra_employee_ds.upload_recom_profile(file_name, file_data, employee_id)
        return res

    @gen.coroutine
    def get_referral_info(self, id):
        ret = yield self.infra_employee_ds.get_referral_info(id)
        return ret

    @gen.coroutine
    def confirm_referral_info(self, data):
        res = yield self.infra_employee_ds.update_referral_info(data)
        return res

    @gen.coroutine
    def get_referral_position_info(self, employee_id, pid, locale=None):
        res = yield self.infra_employee_ds.get_referral_position_info(employee_id, pid)
        if res.status == const.API_SUCCESS:
            data = ObjectDict({
                "job_title": res.data.title,
                "city": ",".join([c.get("name") for c in res.data.cities]),
                "company_abbr": res.data.company_abbreviation,
                "id": res.data.id,
                "job_need": res.data,
                "salary": gen_salary(res.data.salary_top, res.data.salary_bottom),
                "salary_bottom": res.data.salary_bottom,
                "salary_top": res.data.salary_top,
                "experience": gen_experience_v2(str(res.data.experience) if res.data.experience != 0 else "", res.data.experience_above, locale),
                "logo": res.data.logo,
                "team": res.data.team
            })
        else:
            data = ObjectDict()
        return data

    @gen.coroutine
    def update_referral_position(self, employee_id, pid):
        res = yield self.infra_employee_ds.update_referral_position(employee_id, pid)
        return res

    @gen.coroutine
    def update_referral_crucial_info(self, employee_id, params):
        data = ObjectDict({
            "position": params.pid,
            "name": params.realname,
            "gender": params.gender,
            "mobile": params.mobile,
            "email": params.email,
            "company": params.company_name,
            "job": params.position_name,
            "referral_reasons": params.recom_reason,
            "degree": params.degree,
            "city": params.location,
            "recom_reason_text": params.comment,
            "relationship": params.relation,
            "referral_type": 3    # 推荐人才关键信息
        })
        res = yield self.infra_employee_ds.update_referral_crucial_info(employee_id, data)
        return res

    @gen.coroutine
    def get_referral_qrcode(self, url, logo):
        res = yield self.infra_employee_ds.get_referral_qrcode(url, logo)
        return res

    @gen.coroutine
    def get_referral_cards(self, user_id, timestamp, page_number, page_size, company_id):
        """
        十分钟消息模板：卡片数据获取
        :param user_id:   转发职位的员工的user_id
        :param timestamp: 发送消息模板的时间
        :param page_number:
        :param page_size:
        :return:
        """
        res = yield self.infra_employee_ds.get_referral_cards(user_id, timestamp, page_number, page_size, company_id)
        return res

    @gen.coroutine
    def pass_referral_card(self, pid, user_id, company_id, card_user_id, timestamp):
        """
        十分钟消息模板：我不熟悉
        :param pid:
        :param user_id:       转发职位的user_id
        :param company_id:
        :param card_user_id:  当前卡片的user_id
        :param timestamp:     发送消息模板的时间
        :return:
        """
        res = yield self.infra_employee_ds.pass_referral_card(pid, user_id, company_id, card_user_id, timestamp)
        return res

    @gen.coroutine
    def invite_cards_user_apply(self, pid, user_id, company_id, card_user_id, timestamp):
        """
        十分钟消息模板： 邀请投递
        :param pid:
        :param user_id:
        :param card_user_id:
        :param timestamp:
        :return:
        """
        res = yield self.infra_employee_ds.invite_cards_user_apply(pid, user_id, company_id, card_user_id, timestamp)
        return res

    @gen.coroutine
    def invite_cards_invited(self, user_id, candidate_user_id, pid, company_id, timestamp, state):
        """
        邀请投递候选人不在线时，员工点击“人脉连连看”或“转发邀请”时才算已处理过该候选人
        :param user_id:
        :param candidate_user_id:
        :param pid:
        :param company_id:
        :param timestamp:
        :param state:
        :return:
        """
        ret = yield self.infra_employee_ds.invite_cards_invited(user_id, candidate_user_id, pid, company_id, timestamp, state)
        return ret

    @gen.coroutine
    def referral_connections(self, company_id, recom_user_id, end_user_id, chain_id, pid, parent_id):
        """
        人脉连连看
        :param company_id:
        :param recom_user_id: 当前转发用户user_id
        :param end_user_id:   链路结束用户user_id
        :param chain_id:      人脉连连看 链路id
        :param pid: 职位id
        :param parent_id: 父级链路id
        :return:
        """
        res = yield self.infra_employee_ds.referral_connections(
            company_id, recom_user_id, end_user_id, chain_id, pid, parent_id)
        return res

    @gen.coroutine
    def referral_contact_push(self, user_id, position_id):
        """
        联系内推页面获取员工姓名、头像及职位名
        :param user_id:  员工的user_id
        :param position_id:
        :return:
        """
        res = yield self.infra_employee_ds.referral_contact_push(user_id, position_id)
        return res

    @gen.coroutine
    def referral_save_evaluation(self, user_id, company_id, url_params, json_args):
        """
        联系内推： 推荐评价信息保存
        :param user_id:   员工的user_id
        :param company_id:
        :param url_params:
        :param json_args:
        :return:
        """
        params = ObjectDict({
            "company_id": company_id,
            "post_user_id": user_id,
            "position_id": json_args.pid,
            "referral_id": url_params.referral_id,
            "referral_reasons": json_args.recom_reason,
            "recom_reason_text": json_args.comment,
            "relationship": json_args.relation,

        })
        res = yield self.infra_employee_ds.referral_save_evaluation(params)
        return res

    @gen.coroutine
    def nonreferral_save_evaluation(self, user_id, company_id, url_params, json_args):
        """
        联系内推： 推荐评价信息保存
        :param user_id:   员工的user_id
        :param company_id:
        :param url_params:
        :param json_args:
        :return:
        """
        params = ObjectDict({
            "company_id": company_id,
            "post_user_id": user_id,
            "presentee_user_id": url_params.candidate_user_id,
            "position_id": json_args.pid,
            "referral_reasons": json_args.recom_reason,
            "recom_reason_text": json_args.comment,
            "relationship": json_args.relation,

        })
        res = yield self.infra_employee_ds.nonreferral_save_evaluation(params)
        return res

    @gen.coroutine
    def referral_evaluation_page_info(self, company_id, post_user_id, referral_id):
        """
        员工推荐评价页面 候选人和职位信息获取
        :param company_id:
        :param post_user_id:
        :param referral_id:
        :return:
        """
        res = yield self.infra_employee_ds.referral_evaluation_page_info(company_id, post_user_id, referral_id)
        return res

    @gen.coroutine
    def get_referral_progress(self, recom, params):
        """
        员工中心 推荐进度：获取进度列表数据
        :param recom:
        :param params:
        :return:
        """
        ret = yield self.infra_employee_ds.get_referral_progress(params)
        if ret.status == const.API_SUCCESS and ret.data:
            list_data = []
            for item in ret.data:
                list_data.append({
                    "name": item['user']['name'],
                    "user_id": item['user']['uid'],
                    "position_title": item['position']['title'],
                    "position_id": item['position']['pid'],
                    "position_status": item['position']['status'],
                    "datetime": item['datetime'],
                    "category": item.get('progress'),
                    "degree": item.get('degree'),
                    "apply_id": item.get('apply_id'),
                    "referral_origin": {
                        "type": item['recom']['type'],
                        "nickname": item['recom'].get('nickname', ''),
                        "from_wx_group": item['recom'].get('from_wx_group', 0),
                        "referral_id": item['recom'].get('referral_id', 0),
                        "remarked": item['recom'].get('evaluate', 0),
                        "claimed": item['recom'].get('claim', 0),
                        'rkey': item['recom'].get('rkey', 0),
                        'recom': recom
                    }
                })
            data = {'list': list_data}
        else:
            data = ObjectDict()
        return data

    @gen.coroutine
    def get_referral_progress_keyword(self, params):
        """
        员工中心 推荐进度：根据候选人姓名搜索
        :param params:
        :return:
        """
        ret = yield self.infra_employee_ds.get_referral_progress_keyword(params)
        return ret

    @gen.coroutine
    def get_referral_progress_detail(self, apply_id, params):
        """
        员工中心 推荐进度：分享内推进度页面
        :param apply_id:
        :param params:
        :return:
        """
        ret = yield self.infra_employee_ds.get_referral_progress_detail(apply_id, params)
        return ret

    @gen.coroutine
    def get_radar_top_data(self, user_id, company_id):
        """
        获取雷达页面顶部 浏览记录和求推荐数据
        :return:
        """
        ret = yield self.infra_employee_ds.get_radar_top_data(user_id, company_id)
        return ret

    @gen.coroutine
    def get_radar_data(self, user_id, page_size, page_num, company_id):
        """
        获取雷达页面人脉数据
        :return:
        """
        ret = yield self.infra_employee_ds.get_radar_data(user_id, page_size, page_num, company_id)
        return ret

    @gen.coroutine
    def radar_card_position(self, user_id, company_id, pos_title, order, page_num, page_size):
        """
        人脉雷达-分类统计卡-职位浏览
        :return:
        """
        ret = yield self.infra_employee_ds.radar_card_position(user_id, company_id, pos_title, order,
                                                               page_num, page_size)
        data = list()
        if ret.status == const.API_SUCCESS and ret.data:
            for item in ret.data['user_list']:
                data_item = {
                    "avatar": item.get('headimgurl'),
                    "nickname": item.get('nickname'),
                    "degree": item.get('depth'),
                    "position_name": item.get('position_title'),
                    "position_id": item.get('position_id'),
                    "position_status": item.get('status'),
                    "user_id": item.get('user_id'),
                    "datetime": item.get('click_time'),
                    "forward_name": item.get('forward_name'),
                    "forward_source_wx": item.get('forward_source_wx'),
                    "view_count": item.get('view_count'),
                    "invited": item.get('invitation_status'),
                    "connection": item.get('connection'),
                    "chain": item.get('chain'),
                    "chain_status": item.get('chain_status'),
                    "connect_current_uid": 0
                }
                connect_current_uid = 0
                for chain_user in item.get('chain', [])[::-1]:
                    if chain_user.get('pnodes'):
                        connect_current_uid = chain_user.get('uid', 0)
                        break

                data_item.update({
                    "connect_current_uid": connect_current_uid
                })
                data.append(data_item)
        return data

    @gen.coroutine
    def radar_card_seek_recom(self, user_id, company_id, page_num, page_size):
        """
        人脉雷达-分类统计卡-求推荐
        """
        ret = yield self.infra_employee_ds.radar_card_seek_recom(user_id, company_id, page_num, page_size)
        data = list()
        if ret.status == const.API_SUCCESS and ret.data:
            for item in ret.data['user_list']:
                data.append({
                    'avatar': item.get('headimgurl'),
                    'nickname': item.get('nickname'),
                    'degree': item.get('depth'),
                    'position_name': item.get('position_title'),
                    'position_status': item.get('status'),
                    'datetime': item.get('click_time'),
                    'view_count': item.get('view_count'),
                    'forward_name': item.get('forward_name'),
                    'forward_source_wx': item.get('forward_source_wx'),
                    "referral_id": item.get('referral_id'),
                })
        return data
