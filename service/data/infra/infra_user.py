# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
import conf.path as path
from util.common import ObjectDict
from util.tool.http_tool import http_get, http_post, http_put
from util.common.decorator import cache


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
    def post_user_wxbindmobile(self, **kwargs):

        params = ObjectDict({
            "unionid": kwargs["unionid"],
            "mobile": kwargs["mobile"],
            "code": kwargs.get("code" "")
        })

        ret = yield http_post(path.INFRA_USER_COMBINE, params)

        raise gen.Return(ret)

    @gen.coroutine
    def post_wx_pc_combine(self, mobile, unionid):
        """手机号和微信号绑定接口"""

        params = ObjectDict({
            'mobile': mobile,
            'unionid': unionid,
        })

        ret = yield http_post(path.INFRA_USER_COMBINE, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_send_valid_code(self, mobile, type):
        """Request basic service send valid code to target mobile
        :param mobile: target mobile number
        :param type:
        :return:
        """
        params = ObjectDict({
            'mobile': mobile,
            'type': int(type)
        })
        ret = yield http_post(path.INFRA_USER_VALID, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_verify_mobile(self, mobile, code, type):
        """
        Send code submitted by user to basic service.
        :param mobile: target mobile number
        :param code:
        :param type
        :return:
        """
        params = ObjectDict({
            'mobile': mobile,
            'code': code,
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
    def post_register(self, mobile, password):
        """用户注册
        :param mobile: 手机号
        :param password: 密码
        """
        params = ObjectDict(
            username=mobile,
            mobile=mobile,
            password=password,
        )

        ret = yield http_post(path.INFRA_USER_REGISTER, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_ismobileregistered(self, mobile):
        """判断手机号是否已经注册
        :param mobile: 手机号
        """
        params = ObjectDict(
            mobile=mobile,
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
    def post_resetpassword(self, mobile, password):
        """重置密码"""

        params = ObjectDict({
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
            'user_id':        user_id,
            'banner_url':     banner_url,
            'privacy_policy': privacy_policy
        }

        ret = yield http_post(path.INFRA_USER_SETTINGS,params)
        return ret

    @gen.coroutine
    def is_valid_employee(self, user_id, company_id):
        params = {
            "userId": int(user_id),
            "companyId": int(company_id)
        }

        ret = yield http_get(path.INFRA_USER_EMPLOYEE_CHECK, params)

        return ret.result or False
