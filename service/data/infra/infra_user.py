# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing


class InfraUserDataService(DataService):
    """对接 User服务
    referer: https://wiki.moseeker.com/user_account_api.md"""

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""
        params = ObjectDict({
            'user_id': user_id,
        })

        ret = yield http_get(path.INFRA_USER_INFO, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_wx_pc_combine(self, country_code, mobile, unionid):
        """手机号和微信号绑定接口"""

        params = ObjectDict({
            'countryCode': str(country_code),
            'mobile': str(mobile),
            'unionid': str(unionid),
        })

        ret = yield http_post(path.INFRA_USER_COMBINE, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_send_valid_code(self, country_code, mobile, type):
        """Request basic service send valid code to target mobile
        :param country_code: 国家代码
        :param mobile: target mobile number
        :param type:
        :return:
        """
        params = ObjectDict({
            'countryCode': str(country_code),
            'mobile': str(mobile),
            'type': int(type)
        })
        ret = yield http_post(path.INFRA_USER_VALID, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_send_voice_code_for_register(self, mobile):
        """Request basic service send valid voice code to target mobile (only for register)
        :param mobile: target mobile number
        :return:
        """
        params = ObjectDict({
            'mobile': mobile
        })
        ret = yield http_post(path.INFRA_USER_VOICE_VALID, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_verify_mobile(self, country_code, mobile, code, type):
        """
        Send code submitted by user to basic service.
        :param country_code: 国家代码
        :param mobile: target mobile number
        :param code:
        :param type
        :return:
        """
        params = ObjectDict({
            'countryCode': str(country_code),
            'mobile': str(mobile),
            'code': str(code),
            'type': int(type),
        })

        ret = yield http_post(path.INFRA_USER_VERIFY, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_login(self, params):
        """用户登录
        微信 unionid, 或者 mobile+password, 或者mobile+code, 3选1
        :param mobile: 手机号
        :param password: 密码
        :param code: 手机验证码
        :param unionid: 微信 unionid
        """

        ret = yield http_post(path.INFRA_USER_LOGIN, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_logout(self, user_id):
        """用户登出
        :param user_id: 用户 id
        """
        params = ObjectDict(
            user_id=user_id
        )

        ret = yield http_post(path.INFRA_USER_LOGOUT, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_register(self, params):
        """用户注册 """

        ret = yield http_post(path.INFRA_USER_REGISTER, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_ismobileregistered(self, country_code, mobile):
        """判断手机号是否已经注册
        :param country_code: 国家号
        :param mobile: 手机号
        """
        params = ObjectDict(
            countryCode=str(country_code),
            mobile=str(mobile),
        )

        ret = yield http_post(path.INFRA_USER_ISMOBILEREGISTERED, params)
        raise gen.Return(ret)

    @gen.coroutine
    def put_user(self, user_id, req):
        """更新用户信息"""

        params = ObjectDict({
            "id": user_id
        })
        params.update(req)

        ret = yield http_put(path.INFRA_USER_INFO, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_resetpassword(self, country_code, mobile, password):
        """重置密码"""

        params = ObjectDict({
            "countryCode": country_code,
            "mobile": mobile,
            "password": password
        })

        ret = yield http_post(path.INFRA_USER_RESETPASSWD, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_scanresult(self, params):
        """
        设置二维码扫描结果
        :param params:
        :return:
        """

        ret = yield http_post(path.INFRA_WXUSER_QRCODE_SCANRESULT, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_hr_register(self, params):
        """HR用户注册
        :param params
        """

        ret = yield http_post(path.INFRA_HRUSER, params)
        raise gen.Return(ret)

    @gen.coroutine
    def create_user_setting(self, user_id, banner_url='', privacy_policy=0):
        """
        添加帐号设置，user_setting,设置profile的公开度
        :param user_id:
        :param banner_url:
        :param privacy_policy:
        :return: list of dict
        """
        params = {
            'user_id': user_id,
            'banner_url': banner_url,
            'privacy_policy': privacy_policy
        }

        ret = yield http_post(path.INFRA_USER_SETTINGS, params)
        return ret

    @gen.coroutine
    def is_valid_employee(self, user_id, company_id):
        params = {
            "userId": int(user_id),
            "companyId": int(company_id)
        }

        res = yield http_get(path.INFRA_USER_EMPLOYEE_CHECK, params)
        ret, data = unboxing(res)

        return data.result if ret else False

    @gen.coroutine
    def get_employee_survey_info(self, sysuser_id, employee_id):
        params = {
            "id": employee_id,
            "sysuser_id": sysuser_id,
            'activation': const.OLD_YES,
            'disable': const.OLD_YES
        }
        res = yield http_get(path.INFRA_USER_EMPLOYEE, params)
        result, data = unboxing(res)
        if len(data) > 0:
            d = data[0]
        else:
            d = {}
        return result, d

    @gen.coroutine
    def post_employee_survey_info(self, employee_id, survey):
        params = {
            "id": employee_id,
            "position": survey["position"],
            "team_id": survey["department"],
            "job_grade": survey["job_grade"],
            "city_code": survey["city_code"],
            "degree": survey["degree"]
        }
        res = yield http_put(path.INFRA_USER_EMPLOYEE, params)
        return res
