# coding=utf-8

# @Time    : 2/16/17 15:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : email_apply.py
# @DES     :


from app import redis
from app import logger
import conf.common as const


class EmailApplyCache(object):
    """
    email apply 相关
    """

    def __init__(self):
        super(EmailApplyCache, self).__init__()
        # C 端帐号的 session key
        self.session_email_apply = const.FORMAT_EMAIL_CREATE
        self.redis = redis

    def save_email_apply_sessions(self, uuid, value):
        """
        email 申请创建记录缓存
        """

        key = self.session_email_apply.format(uuid)
        self.redis.set(key, value, ttl=60 * 60 * 48, prefix=False)
        logger.debug(
            "save email apply key: {} session: {}".format(
                key, value))

