# coding=utf-8

# @Time    : 1/22/17 11:06
# @Author  : panda (panyuxin@moseeker.com)
# @File    : usercenter.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen

from service.page.base import PageService

class UserCenterPageService(PageService):

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
