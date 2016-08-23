# -*- coding: utf-8 -*-
from cache import BaseCache

class UserCache(BaseCache):

    def __init__(self, redis, prefix='user'):
        super(UserCache, self).__init__(redis, prefix)
