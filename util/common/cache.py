# coding=utf-8

# @Time    : 9/30/16 16:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : redis.py
# @DES     : redis 方法封装

# Copyright 2016 MoSeeker

import json
import redis

from setting import settings
from util.common import ObjectDict
from util.tool.json_tool import json_dumps
from util.tool.str_tool import to_str


class BaseRedis(object):

    _pool = redis.ConnectionPool(
        host=settings["store_options"]["redis_host"],
        port=settings["store_options"]["redis_port"],
        max_connections=settings["store_options"]["max_connections"])

    _redis = redis.StrictRedis(connection_pool=_pool)

    _PREFIX = "WECHAT"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(BaseRedis, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, methods=('get', 'set', 'delete', 'exists')):
        for method_name in methods:
            assert hasattr(self, method_name)

    def key_name(self, key, prefix=True):
        if not prefix:
            return key
        return '{0}_{1}'.format(self._PREFIX, key)

    def _get(self, key, default=None):
        value = to_str(self._redis.get(key))
        if value is None:
            return default
        return json.loads(value)

    def get(self, key, default=None, prefix=True):
        key = self.key_name(key, prefix)
        value = self._get(key, default)
        if isinstance(value, dict):
            return ObjectDict(value)
        elif isinstance(value, list):
            return [ObjectDict(item) for item in value]
        else:
            return default

    def set(self, key, value, ttl=None, prefix=True):
        key = self.key_name(key, prefix)
        value = json_dumps(value)
        self._redis.set(key, value, ex=ttl)

    def update(self, key, value, ttl=None):
        if value is None:
            return

        key = self.key_name(key)
        redis_value = self._get(key)
        if redis_value:
            redis_value.update(value)
            self.set(key, redis_value, ttl)

    def delete(self, key):
        key = self.key_name(key)
        self._redis.delete(key)

    def incr(self, key):
        key = self.key_name(key)
        return self._redis.incr(key)

    def exists(self, key):
        key = self.key_name(key)
        return self._redis.exists(key)
