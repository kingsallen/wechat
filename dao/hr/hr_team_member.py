# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.18
:table hr_team_member

"""

from dao.base import BaseDao


class HrTeamMemberDao(BaseDao):
    def __init__(self, logger):
        super(HrTeamMemberDao, self).__init__(logger)
        self.table = "hr_team_member"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "name": self.constant.TYPE_STRING,  # 成员名称
            "title": self.constant.TYPE_STRING,  # 成员职称
            "description": self.constant.TYPE_STRING,  # 成员描述
            "res_id": self.constant.TYPE_INT,  # 成员头像hr_resource.id
            "team_id": self.constant.TYPE_INT,  # 成员所属团队
            "user_id": self.constant.TYPE_INT,  # 成员对应用户
            "create_time": self.constant.TYPE_TIMESTAMP,  # 创建时间
            "update_time": self.constant.TYPE_TIMESTAMP,  # 更新时间
        }
