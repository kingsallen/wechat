# coding=utf-8

# @Time    : 9/30/16 16:19
# @Author  : panda (panyuxin@moseeker.com)
# @File    : elk.py
# @DES     : redis 给 elk 系统使用

# Copyright 2016 MoSeeker

# import redis
# import os
# from rediscluster import StrictRedisCluster
#
# from setting import settings
# import logging

# class BaseRedisELKCluster(object):
#
#     startup_nodes=[{"host": settings["elk_cluster"]["redis_host"],
#                     "port": port} for port in settings["elk_cluster"]["redis_port"]]
#     redis_cluster = StrictRedisCluster(startup_nodes=startup_nodes)
#
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, '_instance'):
#             orig = super(BaseRedisELKCluster, cls)
#             cls._instance = orig.__new__(cls, *args, **kwargs)
#         return cls._instance
#
#     def __init__(self, methods=('lpush')):
#         for method_name in methods:
#             assert hasattr(self, method_name)
#
#         self.prefix = "wechat" # 待调整
#         logging.debug("pid: %s" % os.getpid())
#
#     def key_name(self, key):
#         return '{0}_{1}'.format(self.prefix, key)
#
#     def lpush(self, key, value):
#         if value is None:
#             return
#
#         key = self.key_name(key)
#         self.redis_cluster.lpush(key, value)

import redis

from setting import settings

class RedisELK(object):

    pool = redis.ConnectionPool(host=settings["elk_cluster"]["redis_host"],
                                port=settings["elk_cluster"]["redis_port"])

    redis = redis.StrictRedis(connection_pool=pool)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(RedisELK, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, methods=('lpush')):
        try:
            self.prefix = "wechat"  # 待调整

            for method_name in methods:
                assert hasattr(self, method_name)

        except Exception as e:
            print e

    def key_name(self, key):
        return '{0}_{1}'.format(self.prefix, key)

    def lpush(self, key, value):
        if value is None:
            return

        key = self.key_name(key)
        self.redis.lpush(key, value)
