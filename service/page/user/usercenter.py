# coding=utf-8

# @Time    : 1/22/17 11:06
# @Author  : panda (panyuxin@moseeker.com)
# @File    : usercenter.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

from service.page.base import PageService

class UsercenterPageService(PageService):

    @gen.coroutine
    def get_user(self, user_id):
        """获得用户数据"""

        ret = yield self.infra_user_ds.get_user(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_applications(self, user_id):
        """获得求职记录"""

        ret = yield self.infra_user_ds.get_applied_applications(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_fav_positions(self, user_id):
        """获得职位收藏"""

        ret = yield self.infra_user_ds.get_fav_positions(user_id)
        raise gen.Return(ret)

    @gen.coroutine
    def update_user(self, user_id, params):
        """更新用户数据"""

        ret = yield self.infra_user_ds.put_user(user_id, params)
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
    def post_register(self, mobile, password, code):
        """用户注册
        :param mobile: 手机号
        :param password: 密码
        :param code: 验证码
        """

        ret = yield self.infra_user_ds.post_register(mobile, password, code)
        raise gen.Return(ret)
