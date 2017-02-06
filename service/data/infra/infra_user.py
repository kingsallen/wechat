# coding=utf-8

import tornado.gen as gen
from util.common import ObjectDict

import conf.path as path

from service.data.base import DataService
from util.tool.http_tool import http_get, http_post, http_put, http_delete, http_patch


class InfraUserDataService(DataService):

    """对接 User服务
    referer: https://wiki.moseeker.com/user_account_api.md"""

    _OPT_TYPE = ObjectDict({
        'code_login':      1,
        'forget_password': 2,
        'modify_info':     3,
        'change_mobile':   4
    })

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""

        params = ObjectDict({
            "user_id": user_id,
        })

        ret = yield http_get(path.USER_INFO, params)
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
            'mobile':  mobile,
            'unionid': unionid,
        })

        ret = yield http_post(path.USER_COMBINE, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_send_valid_code(self, mobile):
        """Request basic service send valid code to target mobile
        :param mobile: target mobile number
        :return:
        """
        params = ObjectDict({
            'mobile': mobile,
            'type':   self._OPT_TYPE.change_mobile,
        })
        ret = yield http_post(path.USER_VALID, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_verify_mobile(self, params):
        """
        Send code submitted by user to basic service.
        :param params: dict include user mobile number and valid code
        :return:
        """
        params = ObjectDict({
            'mobile': params.mobile,
            'code':   params.code,
            'type':   self._OPT_TYPE.change_mobile,
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

        ret = yield http_post(path.USER_LOGIN_PATH, params)
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
