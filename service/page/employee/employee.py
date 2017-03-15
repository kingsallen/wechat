# coding=utf-8

from tornado import gen

from service.page.base import PageService
import conf.common as const
from util.common import ObjectDict
from util.tool.url_tool import make_static_url
from conf.common import YES,NO
from tornado.escape import json_decode, json_encode


class EmployeePageService(PageService):

    def __init__(self):
        super().__init__()

    def show_make_employee_binding_data(self, current_user, conf_response):
        data = ObjectDict()
        data.name = current_user.sysuser.name
        data.headimg = current_user.wxuser.headimg
        data.mobile = current_user.sysuser.mobile
        data.binding_status = YES if current_user.employee else NO
        data.employeeid = current_user.employee.id if data.binding_status else NO
        data.send_hour = 2  # fixed
        conf = conf_response.employeeVerificationConf

        data.conf = ObjectDict()
        data.binding_success_message = conf.bindSuccessMessage or ''

        if conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.DISABLE:
            data.type = 'disabled'
            return data

        if conf.authMode in [const.EMPLOYEE_BIND_AUTH_MODE.EMAIL,
                             const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_CUSTOM,
                             const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_QUESTION]:
            data.type = 'email'
            data.conf.email_name = ""  # fixed
            data.conf.email_suffixs = conf.emailSuffix
            data.conf.email_suffix = data.conf.email_suffixs[0] if len(
                data.conf.email_suffixs) else ''

            if conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_CUSTOM:
                data.conf.switch = 'custom'
                data.conf.custom_hint = conf.customHint
                data.conf.custom_value = ''

            if conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.EMAIL_OR_QUESTION:
                data.conf.switch = 'question'
                data.conf.questions = json_decode(conf)

        elif conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.CUSTOM:
            data.type = 'custom'
            data.conf.custom_hint = conf.customHint
            data.conf.custom_value = ''

        elif conf.authMode == const.EMPLOYEE_BIND_AUTH_MODE.QUESTION:
            data.type = 'question'
            data.conf.questions = json_decode(conf.questions)
        else:
            raise ValueError('invalid authMode')

        return data

    @gen.coroutine
    def get_employee_conf(self, company_id):
        ret = yield self.thrift_employee_ds.get_employee_verification_conf(company_id)
        return ret

    @gen.coroutine
    def get_employee_rewards(self, employee_id, company_id):

        ret = yield self.thrift_employee_ds.get_employee_rewards(employee_id, company_id)
        return ret

    @gen.coroutine
    def unbind(self, employee_id, company_id, user_id):

        ret = yield self.thrift_employee_ds.unbind(employee_id, company_id, user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def bind(self, binding_params):

        ret = yield self.thrift_employee_ds.bind(binding_params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_recommend_records(self, user_id, req_type, page_no, page_size):
        """
        推荐历史记录
        :param user_id:
        :param type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.thrift_useraccounts_ds.get_recommend_records(int(user_id), int(req_type), int(page_no), int(page_size))

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
                    "headimgurl": make_static_url(e.headimgurl or const.SYSUSER_HEADIMG),
                    "is_interested": e.is_interested,
                    "applier_name": e.applier_name,
                    "applier_rel": e.applier_rel,
                    "view_number": e.view_number,
                    "position": e.position,
                    "click_time": e.click_time,
                    "recom_status": e.recom_status
                })
                recommends.append(recom)

        res = ObjectDict({
            "has_recommends": ret.hasRecommends if ret.hasRecommends else False,
            "score": score,
            "recommends": recommends
        })

        raise gen.Return(res)
