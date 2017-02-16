# coding=utf-8

# @Time    : 2/7/17 15:38
# @Author  : panda (panyuxin@moseeker.com)
# @File    : user_hr_account.py
# @DES     :

# Copyright 2016 MoSeeker

from app import redis
from app import logger
import conf.common as const


class UserHrAccountCache(object):
    """
    HR 用户相关 session
    """
    def __init__(self):
        super(UserHrAccountCache, self).__init__()
        # hr帐号的 session key
        self.user_hr_account = const.SESSION_USER_HR_ACCOUNT
        # hr平台绑定微信后的 pub/sub key
        self.wx_binding = const.SESSION_WX_BINDING
        self.redis = redis

    def get_user_hr_account_session(self, hr_id):
        """获得 user_hr_acount 的 session 信息"""
        key = self.user_hr_account.format(hr_id)
        user_hr_account = self.redis.get(key, prefix=False)
        return user_hr_account

    def update_user_hr_account_session(self, hr_id, value):
        """
        更新user_hr_account 的指定元素的 value
        :param hr_id:
        :param value: Dict 形式
        :return:
        """

        if not isinstance(value, dict) or not value:
            return False

        key = self.user_hr_account.format(hr_id)

        logger.debug("[UserHrAccountCache] update_user_hr_account_session key:{0} "
                     "value:{1} type:{2}".format(key, value, type(value)))

        self.redis.update(key, value, ttl=2592000, prefix=False)
        return True

    def del_user_hr_account_session(self, hr_id):
        """删除 user_hr_acount 的 session 信息"""
        key = self.user_hr_account.format(hr_id)
        self.redis.delete(key, prefix=False)
        return True

    def pub_wx_binding(self, hr_id, msg='0'):
        """
        HR招聘管理平台对于HR 帐号绑定微信长轮训机制，需要实时的将状态返回给 HR 平台
        :param hr_id:
        :param msg:
        :return:
        """
        key = self.wx_binding.format(hr_id)
        self.redis.pub(key, msg, prefix=False)
        return True
