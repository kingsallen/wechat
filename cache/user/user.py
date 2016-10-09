# coding=utf-8

# Copyright 2016 MoSeeker

from cache import BaseCache


class UserCache(BaseCache):
    def __init__(self, redis):
        super(UserCache, self).__init__(redis)
