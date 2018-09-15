# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing, http_delete, http_post_multipart_form
from requests.models import Request
from setting import settings
from globals import env


class InfraEmployeeDataService(DataService):
    """对接内推服务"""

    @gen.coroutine
    def get_referral_policy(self, company_id):
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield http_get(path.REFERRAL_POLICY, params)
        return unboxing(ret)

    @gen.coroutine
    def create_interest_policy_count(self, params):
        ret = yield http_post(path.INTEREST_REFERRAL_POLICY, params)
        return unboxing(ret)

    @gen.coroutine
    def get_mate_num(self, company_id):
        ret = yield http_get(path.MATE_NUM.format(company_id))
        return unboxing(ret)

    @gen.coroutine
    def get_unread_praise(self, employee_id):
        ret = yield http_get(path.UNREAD_PRAISE.format(employee_id))
        return unboxing(ret)

    @gen.coroutine
    def vote_prasie(self, employee_id, praise_employee_id):
        ret = yield http_post(path.VOTE_PRAISE.format(employee_id, praise_employee_id))
        return unboxing(ret)

    @gen.coroutine
    def cancel_prasie(self, employee_id, praise_employee_id):
        ret = yield http_delete(path.VOTE_PRAISE.format(employee_id, praise_employee_id))
        return unboxing(ret)

    @gen.coroutine
    def get_last_rank_info(self, employee_id, type):
        params = ObjectDict({
            "type": type
        })
        ret = yield http_get(path.LAST_RANK_INFO.format(employee_id), params)
        return unboxing(ret)

    @gen.coroutine
    def get_current_user_rank_info(self, employee_id, type):
        params = ObjectDict({
            "type": type
        })
        ret = yield http_get(path.USER_RANK_INFO.format(employee_id), params)
        return unboxing(ret)

    @gen.coroutine
    def get_award_ladder_type(self, company_id):
        ret = yield http_get(path.LADDER_TYPE.format(company_id))
        return unboxing(ret)

    @gen.coroutine
    def get_bind_reward(self, company_id):
        params = ObjectDict({
            "companyId": company_id
        })
        ret = yield http_get(path.BIND_REWARD, params)
        return unboxing(ret)

    @gen.coroutine
    def upload_recom_profile(self, file_name, file_data, employee_id):
        url = "{0}/{1}".format(settings['infra'], path.UPLOAD_RECOM_PROFILE)
        request = Request(data={
            "employee": employee_id,
            "appid": const.APPID[env]},
            files={
                "file": (file_name, file_data)
            },
            url=url,
            method="POST"
        )
        p = request.prepare()
        body = p.body
        headers = p.headers

        ret = http_post_multipart_form(url, body, headers=headers)
        return ret

    @gen.coroutine
    def get_referral_info(self, id):
        ret = yield http_get(path.REFERRAL_INFO.format(id))
        return ret

    @gen.coroutine
    def update_referral_info(self, params):
        ret = yield http_post(path.INFRA_REFERRAL_CONFIRM, params)
        return ret

    @gen.coroutine
    def get_referral_position_info(self, employee_id, pid):
        params = ObjectDict({
            "position": pid
        })
        ret = yield http_get(path.REFERRAL_POSITION_INFO_EMPLOYEE.format(employee_id), params)
        return ret

    @gen.coroutine
    def update_referral_position(self, employee_id, pid):
        params = ObjectDict({
            "position": pid
        })
        ret = yield http_post(path.REFERRAL_POSITION_INFO_EMPLOYEE.format(employee_id), params)
        return ret

    @gen.coroutine
    def update_referral_crucial_info(self, employee_id, params):
        ret = yield http_post(path.INFRA_REFERRAL_CRUCIAL_INFO.format(employee_id), params)
        return ret

    @gen.coroutine
    def get_referral_qrcode(self, url, logo):
        params = ObjectDict({
            "url": url,
            "logo": logo
        })
        ret = yield http_post(path.REFERRAL_QRCODE, params)
        return ret

    @gen.coroutine
    def get_employee_by_user_id(self, user_id):
        ret = yield http_get(path.INFRA_USER_EMPLOYEE_REFERRAL.format(user_id))
        return ret
