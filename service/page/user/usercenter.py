# coding=utf-8

# @Time    : 1/22/17 11:06
# @Author  : panda (panyuxin@moseeker.com)
# @File    : usercenter.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

from service.page.base import PageService

from thrift_gen.gen.useraccounts.service.UserCenterService import Client as UserCenterServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF

class UsercenterPageService(PageService):

    usercenter_service_cilent = ServiceClientFactory.get_service(
        UserCenterServiceClient, CONF)

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""

        ret = yield self.infra_user_ds.get_user(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def update_user(self, user_id, params):
        """更新用户数据"""

        ret = yield self.infra_user_ds.put_user(user_id, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_resetpassword(self, mobile, password):
        """重置密码"""

        ret = yield self.infra_user_ds.post_resetpassword(mobile, password)
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

        ret = yield self.infra_user_ds.post_login(params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_logout(self, user_id):
        """用户登出
        :param user_id:
        """

        ret = yield self.infra_user_ds.post_logout(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def post_register(self, mobile, password):
        """用户注册
        :param mobile: 手机号
        :param password: 密码
        """

        ret = yield self.infra_user_ds.post_register(mobile, password)
        raise gen.Return(ret)

    @gen.coroutine
    def post_ismobileregistered(self, mobile):
        """判断手机号是否已经注册
        :param mobile: 手机号
        """

        ret = yield self.infra_user_ds.post_ismobileregistered(mobile)
        raise gen.Return(ret)

    @gen.coroutine
    def get_fav_positions(self, user_id):
        """获得职位收藏"""

        ret = yield self.thrift_useraccounts_ds.get_fav_positions(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_applications(self, user_id):
        """获得求职记录"""

        ret = yield self.thrift_useraccounts_ds.get_applied_applications(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_progress(self, app_id, user_id):
        """
        求职记录中的求职详情进度
        :param app_id:
        :param user_id:
        :return:
        """
        ret = yield self.thrift_useraccounts_ds.get_applied_progress(app_id, user_id)
        raise gen.Return(ret)
