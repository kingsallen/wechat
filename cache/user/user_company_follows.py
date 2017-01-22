# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

import json
from util.common.cache import BaseRedis


# todo (tangyiliang): 关注关系未加缓存，这块以后是否要使用？
class UserCompanyFollowsCache(BaseRedis):
    """
    Develop Status: To be tested.
    """
    def __init__(self, redis):
        super(UserCompanyFollowsCache, self).__init__(redis)
        self.company_fans_hash = '{0}_company_fans'.format(self._PREFIX)
        self.following_companys_hash = '{0}_following_companys'.format(
                                       self._PREFIX)

    def _fan_key(self, cmpy_id):
        return 'company_fan:{0}'.format(cmpy_id)

    def _company_key(self, user_id):
        return 'following_company:{0}'.format(user_id)

    def get_company_fans(self, cmpy_id):
        key = self._fan_key(cmpy_id)
        fans = self._redis.hget(self.company_fans_hash, key)
        if fans is None:
            return fans
        return json.loads(fans)

    def get_following_companys(self, user_id):
        key = self._company_key(user_id)
        companys = self._redis.hget(self.following_companys_hash, key)
        if companys is None:
            return companys
        return json.loads(companys)

    def set_company_fans(self, cmpy_id, user_id, timestamp):
        key = self._fan_key(cmpy_id)
        fans = self.get_company_fans(cmpy_id)
        new_fans = fans if fans else {}
        fans[str(user_id)] = timestamp
        self._redis.hset(self.company_fans_hash, key, json.dumps(new_fans))

    def set_following_companys(self, user_id, cmpy_id, timestamp):
        key = self._company_key(user_id)
        companys = self.get_following_companys(user_id)
        new_companys = companys if companys else {}
        new_companys[str(cmpy_id)] = timestamp
        self._redis.hset(self.following_companys_hash, key,
                         json.dumps(new_companys))

    def delete_company_fan(self, cmpy_id, user_id):
        key = self._fan_key(cmpy_id)
        if self._redis.hexists(self.company_fans_hash, key):
            fans = self.get_company_fans(cmpy_id)
            if fans and str(user_id) in fans.keys():
                fans.pop(str(user_id))
                self._redis.hset(self.company_fans_hash, key,
                                 json.dumps(fans))

    def delete_following_companys(self, user_id, cmpy_id):
        key = self._company_key(user_id)
        if self._redis.hexists(self.following_companys_hash, key):
            companys = self.get_following_companys(user_id)
            if companys and str(cmpy_id) in companys.keys():
                companys.pop(str(cmpy_id))
                self._redis.hset(self.following_companys_hash, key,
                                 json.dumps(companys))
