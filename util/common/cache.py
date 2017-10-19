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

from json import JSONDecodeError

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

    def get_raw_redis_client(self):
        return self._redis

    def key_name(self, key, prefix=True):
        if not prefix:
            return key
        return '{0}_{1}'.format(self._PREFIX, key)

    def _get(self, key, default=None):
        value = to_str(self._redis.get(key))
        ret = None

        if value is None:
            return default

        try:
            ret = json.loads(value)

        except JSONDecodeError as e:
            # 如果 value 不符合 JSON 格式，则直接返回
            ret = value

        except TypeError as e:
            print(e)
            print('key: %s, value: %s' % (key, value))
            raise e
        finally:
            return ret

    def get(self, key, default=None, prefix=True):

        key = self.key_name(key, prefix)
        value = self._get(key, default)

        if isinstance(value, dict):
            return ObjectDict(value)

        elif isinstance(value, list):
            return [ObjectDict(item) for item in value]

        elif isinstance(value, str):
            mapping = {'True': True, 'False': False}
            if value in mapping:
                return mapping[value]
            else:
                return value

        return default

    def set(self, key, value, ttl=None, prefix=True):
        key = self.key_name(key, prefix)
        if isinstance(value, (dict, list)):
            value = json_dumps(value)

        self._redis.set(key, value, ex=ttl)

    def update(self, key, value, ttl=None, prefix=False):
        if value is None:
            return
        key = self.key_name(key, prefix)
        redis_value = self._get(key)
        if redis_value:
            redis_value.update(value)
            self.set(key, redis_value, ttl, prefix=prefix)

    def delete(self, key, prefix=True):
        key = self.key_name(key, prefix)
        self._redis.delete(key)

    def incr(self, key, prefix=True):
        key = self.key_name(key, prefix)
        return self._redis.incr(key)

    def exists(self, key):
        key = self.key_name(key)
        return self._redis.exists(key)

    def pub(self, key, message, prefix=True):
        channel = self.key_name(key, prefix)
        return self._redis.publish(channel, message)

if __name__ == "__main__":

    redis = BaseRedis()

    key = "aaa"
    value1 = {
        "a": 1,
        "b": {}
    }

    # res = redis.set(key, value1, ttl=3333, prefix=False)

    value2 = {
        "a": 2,
        "b": {
            "bbb": 7
        }
    }

    res = redis.update(key, value2, prefix=False)
    print (redis.get(key, prefix=False))
