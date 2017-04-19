# coding=utf-8

import json
from tornado import gen

import conf.common as const
import conf.fe as fe
import conf.path as path
from setting import settings

from service.page.base import PageService
from thrift_gen.gen.employee.struct.ttypes import BindingParams, BindStatus
from util.common import ObjectDict
from util.tool.dict_tool import sub_dict
from util.tool.url_tool import make_static_url, make_url
from util.wechat.template import employee_refine_custom_fields_tpl


class EmployeePageService(PageService):

    FE_BIND_STATUS_SUCCESS = 0
    FE_BIND_STATUS_UNBINDING = 1
    FE_BIND_STATUS_NEED_VALIDATE = 2
    FE_BIND_STATUS_FAILURE = 3

    FE_BIND_TYPE_CUSTOM = 'custom'
    FE_BIND_TYPE_EMAIL = 'email'
    FE_BIND_TYPE_QUESTION = 'question'

    BIND_AUTH_MODE = ObjectDict({
        FE_BIND_TYPE_EMAIL:    0,
        FE_BIND_TYPE_CUSTOM:   1,
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
            'activation':      const.OLD_YES,
            'disable':         const.OLD_YES,
            'status':          const.OLD_YES
        })
        return record

    @gen.coroutine
    def get_employee_info(self, user_id, company_id):
        """获取员工信息"""
        employee_response = yield self.thrift_employee_ds.get_employee(
            user_id, company_id)
        return employee_response.bindStatus, employee_response.employee

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
            assert False  # should not be here

        return fe_bind_status

    @gen.coroutine
    def get_employee_bind_status(self, user_id, company_id):
        """获取员工绑定状态"""
        bind_status, _ = yield self.get_employee_info(user_id, company_id)
        return bind_status

    @gen.coroutine
    def make_binding_render_data(self, current_user, conf):
        """构建员工绑定页面的渲染数据
        :returns:
        {
            'type':            'email',
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
            }
        """

        data = ObjectDict()
        data.name = current_user.sysuser.name
        data.headimg = current_user.sysuser.headimg
        data.mobile = current_user.sysuser.mobile or ''
        data.send_hour = 24  # fixed
        data.conf = ObjectDict()
        data.binding_success_message = conf.bindSuccessMessage or ''

        bind_status, employee = yield self.get_employee_info(
            user_id=current_user.sysuser.id, company_id=current_user.company.id)

        # 当前是绑定状态
        if bind_status == BindStatus.BINDED:
            data.binding_status = self.FE_BIND_STATUS_SUCCESS
            data.employeeid = employee.id
            data.name = employee.cname

        # 当前是未绑定状态
        else:
            # 否则，调用基础服务判断当前用户的认证状态：没有认证还是 pending 中
            data.employeeid = const.NO

            if bind_status == const.EMPLOYEE_BIND_STATUS_UNBINDING:
                data.binding_status = self.FE_BIND_STATUS_UNBINDING

            elif bind_status == const.EMPLOYEE_BIND_STATUS_EMAIL_PENDING:
                data.binding_status = self.FE_BIND_STATUS_NEED_VALIDATE

            else:
                data.binding_status = self.FE_BIND_STATUS_FAILURE

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

                # 初始化 email_name, email_suffix 为空字符串
                # 随后根据员工的 email 填写数据
                data.conf.email_name = ''
                data.conf.email_suffix = ''
                self.logger.debug(employee.email)
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
                assert False # should not be here

        # 未绑定的员工， 根据 conf.authMode 来渲染
        else:
            if conf.authMode in [const.EMPLOYEE_BIND_AUTH_MODE.EMAIL,
                                 const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_CUSTOM,
                                 const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_QUESTION]:
                data.type = self.FE_BIND_TYPE_EMAIL
                data.conf.email_suffixs = conf.emailSuffix
                if bind_status in [const.EMPLOYEE_BIND_STATUS_BINDED,
                                   const.EMPLOYEE_BIND_STATUS_EMAIL_PENDING]:
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

        self.logger.debug('binding_render_data: %s' % data)
        return data

    def make_bind_params(self, user_id, company_id, json_args):
        """
        构建员工绑定的参数集合
        :param user_id:
        :param company_id:
        :param json_args:
        :return:
        """
        type = json_args.type

        needed_keys = ['type', 'name', 'mobile']

        if type == self.FE_BIND_TYPE_CUSTOM:
            needed_keys.append('custom_value')
        elif type == self.FE_BIND_TYPE_EMAIL:
            needed_keys.append('email_name')
            needed_keys.append('email_suffix')
        elif type == self.FE_BIND_TYPE_QUESTION:
            needed_keys.append('answers')

        param_dict = sub_dict(json_args, needed_keys)

        if type == self.FE_BIND_TYPE_EMAIL:
            param_dict.email = '%s@%s' % (param_dict.email_name, param_dict.email_suffix)
        if type == self.FE_BIND_TYPE_QUESTION:
            param_dict.answer1 = param_dict.answers[0]
            if len(param_dict.answers) > 1:
                param_dict.answer2 = param_dict.answers[1]
            else:
                param_dict.answer2 = ''

        binding_params = BindingParams(
            type=self.BIND_AUTH_MODE[param_dict.type],
            userId=user_id,
            companyId=company_id,
            email=param_dict.email,
            mobile=str(param_dict.mobile),
            customField=param_dict.custom_value,
            name=param_dict.name,
            answer1=param_dict.answer1,
            answer2=param_dict.answer2)

        return binding_params

    @gen.coroutine
    def get_employee_conf(self, company_id):
        """获取员工绑定配置"""
        ret = yield self.thrift_employee_ds.get_employee_verification_conf(
            company_id)
        return ret

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):
        """获取员工积分信息"""
        ret = yield self.thrift_employee_ds.get_employee_rewards(
            employee_id, company_id)
        return ret

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
    def activate_email(self, activation_code):
        """通过邮箱激活员工"""
        ret = yield self.thrift_employee_ds.activate_email(activation_code)
        return ret.success, ret.message

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
                "interested_count":  ret.score.interested_count,
                "applied_count":     ret.score.applied_count
            })
        recommends = list()
        if ret.recommends:
            for e in ret.recommends:
                recom = ObjectDict({
                    "status":        e.status,
                    "headimgurl":    make_static_url(
                        e.headimgurl or const.SYSUSER_HEADIMG),
                    "is_interested": e.is_interested,
                    "applier_name":  e.applier_name,
                    "applier_rel":   e.applier_rel,
                    "view_number":   e.view_number,
                    "position":      e.position,
                    "click_time":    e.click_time,
                    "recom_status":  e.recom_status
                })
                recommends.append(recom)

        res = ObjectDict({
            "has_recommends": ret.hasRecommends if ret.hasRecommends else False,
            "score":          score,
            "recommends":     recommends
        })

        raise gen.Return(res)

    @gen.coroutine
    def get_employee_custom_fields(self, company_id):
        """
        根据公司 id 返回员工认证自定义字段配置 -> list
        并按照 forder 字段排序返回
        """
        selects_from_ds = yield self.hr_employee_custom_fields_ds.\
            get_employee_custom_field_records({
                "company_id": company_id,
                "status": const.OLD_YES,
                "disable": const.NO
            })

        selects = sorted(selects_from_ds, key=lambda x: x.forder)

        for s in selects:
            s.fvalues = json.loads(s.fvalues)
            s.required = s.mandatory == const.YES
        return selects

    @gen.coroutine
    def update_employee_custom_fields(self, employee_id, custom_fields_json):
        """
        更新员工记录 custom_fields
        :param employee_id:
        :param custom_fields_json:
        :return:
        """

        ret = yield self.user_employee_ds.update_employee(
            conds={ 'id': employee_id },
            fields={'custom_field_values': custom_fields_json}
        )

        return ret

    @gen.coroutine
    def send_emp_custom_info_template(self, current_user):
        """发送员工认证自定义字段填写template
        """

        if current_user.wxuser:
            company_id = current_user.company.id
            custom_fields = yield self.get_employee_custom_fields(company_id)

            self.logger.debug("custom_fields: %s" % custom_fields)

            if not custom_fields:
                return

            link = make_url(path.EMPLOYEE_CUSTOMINFO,
                            host=settings['platform_host'],
                            wechat_signature=current_user.wechat.signature,
                            from_wx_template='o')

            yield employee_refine_custom_fields_tpl(
                wechat_id=current_user.wechat.id,
                openid=current_user.wxuser.openid,
                link=link,
                company_name=current_user.company.name
            )
