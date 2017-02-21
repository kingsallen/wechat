# coding=utf-8

# @Time    : 2/16/17 15:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : passport_session.py
# @DES     :

# Copyright 2016 MoSeeker

from app import redis
from app import logger
import conf.common as const
from setting import settings
from util.common import ObjectDict


class PassportCache(object):
    """
    C端用户相关 Session
    """

    def __init__(self):
        super(PassportCache, self).__init__()
        # C 端帐号的 session key
        self.session_user = const.SESSION_USER
        self.redis = redis
        self.settings = settings

    def save_qx_sessions(self, session_id, qxuser):
        """
        保存聚合号 session， 只包含 qxuser
        """

        key_qx = self.session_user.format(
            session_id, self.settings['qx_wechat_id'])
        self.redis.set(key_qx, ObjectDict(qxuser=qxuser), 60 * 60 * 24 * 30)
        logger.debug(
            "refresh qx session redis key: {} session: {}".format(
                key_qx, ObjectDict(
                    qxuser=qxuser)))

    def save_ent_sessions(self, session_id, session, wechat_id):
        """
        保存企业号 session， 包含 wxuser, qxuser
        """

        key_ent = self.session_user.format(session_id, wechat_id)
        self.redis.set(key_ent, session, 60 * 60 * 2)
        logger.debug(
            "refresh ent session redis key: {} session: {}".format(
                key_ent, session))

    def clear_session(self, session_id, wechat_id):
        """情况用户所用的 session"""

        key_ent = self.session_user.format(session_id, wechat_id)
        self.redis.delete(key_ent)
        logger.debug("delete ent session redis key: {}".format(key_ent))
