# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 赵中华（zhaozhonghua@moseeker.com）
:date 2016.08.30
"""

import hashlib
import redis
import json

from functools import wraps
from utils.tool.json_tool import json_dumps
from tornado import gen
from tornado.util import ObjectDict
from tornado.locks import Semaphore

from setting import settings

sem = Semaphore(1)

class BaseCache(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(BaseCache, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, redis=None, prefix='neoweixinrefer', methods=('get', 'set', 'delete', 'exists')):

        for method_name in methods:
            assert hasattr(redis, method_name)

        self.__redis = redis
        self.prefix = prefix

    def key_name(self, key):
        return '{0}:{1}'.format(self.prefix, key)

    def _get(self, key, default=None):
        value = self.__redis.get(key)
        if value is None:
            return default
        return json.loads(value)

    def get(self, key, default=None):
        key = self.key_name(key)
        value = self._get(key, default)
        if isinstance(value, ObjectDict) or isinstance(value, dict):
            return ObjectDict(value)
        elif isinstance(value, list):
            return [ObjectDict(item) for item in value]
        else:
            return default

    def set(self, key, value, ttl=None):
        key = self.key_name(key)
        value = json_dumps(value)
        self.__redis.set(key, value, ex=ttl)

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
        self.__redis.delete(key)

    def exists(self, key):
        key = self.key_name(key)
        return self.__redis.exists(key)


pool = redis.ConnectionPool(host= settings["store_options"]["redis_host"],
                            port= settings["store_options"]["redis_port"],
                            max_connections= settings["store_options"]["max_connections"])

redis = redis.StrictRedis(connection_pool=pool)

base_cache = BaseCache(redis=redis)

def cache(prefix=None, key=None, ttl=60, hash=True, lock=True, separator=":"):
    """
    cache装饰器

    :param prefix: 指定prefix
    :param key: 指定key
    :param timeout: ttl (s)
    :param hash: 是否需要hash
    :param lock: -
    :return:
    """
    key_ = key
    ttl_ = ttl
    hash_ = hash
    lock_ = lock
    prefix_ = prefix
    separator_ = separator

    def cache_inner(func):

        key, ttl, hash, lock, prefix, separator = key_, ttl_, hash_, lock_, prefix_, separator_

        prefix = prefix if prefix else "{0}:{1}".format(func.__module__.split(".")[-1], func.__name__)

        @wraps(func)
        @gen.coroutine
        def func_wrapper(*args, **kwargs):

            if lock:
                yield sem.acquire()

            try:
                if not key:

                    redis_key = None

                    if args and len(args) > 1:
                        redis_key = separator.join([str(_) for _ in list(args[1].values())])

                    if kwargs:
                        spliter = separator if redis_key else ""
                        redis_key = redis_key + spliter + separator.join([str(_) for _ in list(kwargs.values())])
                else:
                     redis_key = key

                if hash:
                    redis_key = hashlib.md5(redis_key.encode("utf-8")).hexdigest()

                redis_key = "{prefix}{separator}{redis_key}".format(prefix=prefix, separator=separator, redis_key=redis_key)

                if base_cache.exists(redis_key):
                    cache_data = base_cache.get(redis_key)
                else:
                    cache_data = yield func(*args, **kwargs)
                    base_cache.set(redis_key, cache_data, ttl)

                raise gen.Return(cache_data)

            finally:
                if lock:
                    sem.release()

        return func_wrapper

    return cache_inner
