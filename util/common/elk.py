# coding=utf-8

# @Time    : 9/30/16 16:19
# @Author  : panda (panyuxin@moseeker.com)
# @File    : elk.py
# @DES     : redis 给 elk 系统使用

# Copyright 2016 MoSeeker

import redis

from abc import ABCMeta, abstractmethod
from tornado.options import options

from setting import settings
import conf.common as constant


class IMessageSendable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_message(self, key, value):
        pass


class RedisELK(IMessageSendable):
    """A logger implementation sending message to redis server"""

    pool = redis.ConnectionPool(host=settings["elk_cluster"]["redis_host"],
                                port=settings["elk_cluster"]["redis_port"])

    redis = redis.StrictRedis(connection_pool=pool)

    _KEY_PREFIX = "log"  # elk只能接受小写的 key
    _APPID = constant.APPID[options.env]

    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            orig = super(RedisELK, cls)
            cls._instance = orig.__new__(cls, *args)
        return cls._instance

    def __init__(self, methods=('send_message')):
        try:
            for method_name in methods:
                assert hasattr(self, method_name)
        except Exception as e:
            print(e)

    def key_name(self, key):
        return '{0}_{1}_{2}'.format(self._KEY_PREFIX, self._APPID, key)

    def send_message(self, key, value):
        if value and key:
            key = self.key_name(key)
            self.redis.lpush(key, value)
