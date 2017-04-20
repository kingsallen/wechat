# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.09
:table user_company_follow

"""

from dao.base import BaseDao


class UserCompanyFollowDao(BaseDao):

    def __init__(self):
        super(UserCompanyFollowDao, self).__init__()
        self.table = 'user_company_follow'
        self.fields_map = {
            "id":             self.constant.TYPE_INT,
            "company_id":     self.constant.TYPE_INT,
            "user_id":        self.constant.TYPE_INT,
            # 是否关注 0：取消关注，1：关注'
            "status":         self.constant.TYPE_INT,
            # 关注操作来源 0: 未知，1：微信端，2：PC 端
            "source":         self.constant.TYPE_INT,
            # 关注时间
            "create_time":    self.constant.TYPE_TIMESTAMP,
            # 更新时间
            "update_time":    self.constant.TYPE_TIMESTAMP,
            # 取消关注时间
            "unfollow_time":  self.constant.TYPE_TIMESTAMP,
        }
