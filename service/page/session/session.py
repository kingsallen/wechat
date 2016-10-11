# coding=utf-8

import os
import time
from hashlib import sha1

from tornado import gen

import conf.common as const
from service.page.base import PageService


class SessionPageService(PageService):

    @gen.coroutine
    def create_or_update_wxuser(self, userinfo, wechat_id):
        # 1. 按照userinfo.openid 和 wechat_id 尝试获取 wxuser
        wxuser = yield self.user_wx_user_ds.get_wxuser(openid=userinfo.openid, wechat_id=wechat_id)
        # 2. 如果没有 新建
        # 3. 如果有 更新
        if not wxuser:
            yield self.user_wx_user_ds.create_wxuser(userinfo, wechat_id)
        else:
            yield self.user_wx_user_ds.update_wxuser(userinfo, wechat_id)
