# coding=utf-8

# @Time    : 2/16/17 15:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : chat_session.py
# @DES     :

from globals import redis
from globals import logger
import conf.common as const


class ChatCache(object):
    """
    聊天 Session
    """

    def __init__(self):
        super(ChatCache, self).__init__()
        # C 端帐号的 session key
        self.session_key = const.CHAT_CHATROOM_ENTER
        self.redis = redis

    def mark_enter_chatroom(self, user_id):
        """
        标记用户进入聊天室
        """

        key = self.session_key.format(user_id)
        self.redis.incr(key, prefix=False)
        logger.debug("mark_enter_chatroom key: {}".format(key))

    def mark_leave_chatroom(self, user_id):
        """
        标记用户离开聊天室
        """

        key = self.session_key.format(user_id)
        self.redis.delete(key, prefix=False)
        logger.debug("mark_leave_chatroom key: {}".format(key))
