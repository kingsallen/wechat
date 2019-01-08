# coding=utf-8

import tornado.gen as gen

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put, unboxing
from util.common.decorator import log_time


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
    def get_my_info(self, user_id, params):
        """获得用户我的个人中心数据"""
        ret = yield http_get(path.INFRA_MY_INFO.format(user_id), params)
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
    def post_ismobileregistered(self, mobile, country_code=86):
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

    @log_time
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

    @gen.coroutine
    def update_recommend(self, params, employee_id):
        res = yield http_post(path.UPDATE_RECOMMEND.format(employee_id), params)
        return res

    @gen.coroutine
    def get_applied_applications(self, user_id, company_id):
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id
        })
        res = yield http_get(path.INFRA_USER_APPLYRECORD, params)
        return res

    @gen.coroutine
    def get_redpacket_list(self, user_id, params):
        res = yield http_get(path.INFRA_USER_REDPACKET_LIST.format(user_id), params)
        return res

    @gen.coroutine
    def get_bonus_list(self, user_id, params):
        res = yield http_get(path.INFRA_USER_BONUS_LIST.format(user_id), params)
        return res

    @gen.coroutine
    def claim_bonus(self, bonus_id):
        res = yield http_put(path.INFRA_USER_CLAIM_BONUS.format(bonus_id))
        return res

    @gen.coroutine
    def get_popup_info(self, user_id, company_id, position_id):
        """
        候选人进入职位详情弹层数据接口
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id,
            "position_id": position_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_POPUP, params)
        return ret

    @gen.coroutine
    def close_popup_window(self, user_id, company_id, type):
        """
        候选人职位详情弹层关闭
        :param user_id:
        :param company_id:
        :param type: int   0 二维码弹层 1 简历完善度弹层
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id,
            "type": type
        })
        ret = yield http_put(path.INFRA_REFERRAL_CLOSE_POPUP_WINDOW, params)
        return ret

    @gen.coroutine
    def referral_confirm_submit(self, user_id, post_user_id, position_id, origin):
        """
        候选人联系内推：简历预览页面确认提交
        :param user_id:  候选人id
        :param post_user_id: 最初转发职位的员工的user_id
        :param position_id:
        :param origin: 申请来源，1 转发，2 连连看
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "post_user_id": post_user_id,
            "position_id": position_id,
            "origin": origin
        })
        ret = yield http_post(path.INFRA_REFERRAL_CONTACT_PUSH, params)
        return ret

    @gen.coroutine
    def referral_related_positions(self, user_id, company_id):
        """
        候选人联系内推完成页面推荐三个相关职位信息
        :param user_id:
        :param company_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id
        })
        ret = yield http_get(path.INFRA_REFERRAL_RELATIVE_POSITIONS, params)
        return ret

    @gen.coroutine
    def if_referral_position(self, recom, psc, pid):
        """
        候选人打开转发的职位链接，根据链接中参数判断最初转发该职位的人是否是员工
        :param recom:  直接转发人的user_id
        :param psc:   父级链路id   candidate_share_chain.id
        :param pid:
        :return:
        """
        params = ObjectDict({
            "recom_user_id": recom,
            "parent_chain_id": psc,
            "pid": pid
        })
        ret = yield http_post(path.INFRA_IF_EMPLOYEE_POS, params)
        return ret
