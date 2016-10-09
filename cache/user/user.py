# coding=utf-8

# Copyright 2016 MoSeeker

from utils.common.cache import BaseRedis

class UserCache(BaseCache):
    def __init__(self, redis):
        super(UserCache, self).__init__(redis)
