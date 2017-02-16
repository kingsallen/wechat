# coding=utf-8

from service.data.base import DataService
import tornado.gen as gen
from util.common import ObjectDict
import conf.path as path
from util.tool.http_tool import http_get, http_post, http_put, http_delete, http_patch


class InfraUserDataService(DataService):

    """对接 User服务
    referer: https://wiki.moseeker.com/user_account_api.md"""

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""
        params = ObjectDict({
            'user_id': user_id,
        })

        ret = yield http_get(path.USER_INFO, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_user_wxbindmobile(self, **kwargs):

        params = ObjectDict({
            "unionid": kwargs["unionid"],
            "mobile": kwargs["mobile"],
            "code": kwargs.get("code" "")
        })

        ret = yield http_post(path.USER_COMBINE, params)

        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_applications(self, user_id):
        """获得求职记录"""
        ret = yield http_get(path.USER_APPLIED_APPLICATIONS.format(user_id))
        raise gen.Return(ret)

    @gen.coroutine
    def get_fav_positions(self, user_id):
        """获得职位收藏"""

        ret = yield http_get(path.USER_FAV_POSITION.format(user_id))
        raise gen.Return(ret)

    @gen.coroutine
    def post_wx_pc_combine(self, mobile, unionid):
        """手机号和微信号绑定接口"""

        params = ObjectDict({
            'mobile': mobile,
            'unionid': unionid,
        })

        ret = yield http_post(path.USER_COMBINE, params)
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
            'type': type
        })
        ret = yield http_post(path.USER_VALID, params)
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
            'type': type,
        })

        ret = yield http_post(path.USER_VERIFY, params)
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

        ret = yield http_post(path.USER_LOGIN, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_logout(self, user_id):
        """用户登出
        :param user_id: 用户 id
        """
        params = ObjectDict(
            user_id=user_id
        )

        ret = yield http_post(path.USER_LOGOUT, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_register(self, mobile, password, code):
        """用户注册
        :param mobile: 手机号
        :param password: 密码
        """
        params = ObjectDict(
            username=mobile,
            mobile=mobile,
            password=password,
            code=code
        )

        ret = yield http_post(path.USER_REGISTER, params)
        raise gen.Return(ret)

    @gen.coroutine
    def put_user(self, user_id, req):
        """更新用户信息"""

        params = ObjectDict({
            "id": user_id
        })
        params.update(req)

        ret = yield http_put(path.USER_INFO, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_scanresult(self, params):
        """
        设置二维码扫描结果
        :param params:
        :return:
        """

        ret = yield http_post(path.WXUSER_QRCODE_SCANRESULT, params)
        raise gen.Return(ret)
