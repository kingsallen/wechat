# coding=utf-8
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.18
:table hr_team

"""

from dao.base import BaseDao


class HrTeamDao(BaseDao):
    def __init__(self):
        super(HrTeamDao, self).__init__()
        self.table = "hr_team"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "name": self.constant.TYPE_STRING,  # 团队名称
            "summary": self.constant.TYPE_STRING,  # 职能概述
            "description": self.constant.TYPE_STRING,  # 团队介绍
            "show_order": self.constant.TYPE_INT,  # 团队列表顺序
            "res_id": self.constant.TYPE_INT,  # 团队主图片 hr_resource.id
            "jd_media": self.constant.TYPE_STRING,  # JD页团队信息hr_media.id: [1, 23, 32]
            "team_detail": self.constant.TYPE_STRING,  # 团队详情hr_media.id: [34, 35]
            "slogan": self.constant.TYPE_STRING,  # 团队口号
            "is_show": self.constant.TYPE_INT,  # 团队是否显示（列表页，other team） 0：不显示，1：显示
            "company_id": self.constant.TYPE_INT,  # 团队所在母公司
            "create_time": self.constant.TYPE_TIMESTAMP,  # 创建时间
            "update_time": self.constant.TYPE_TIMESTAMP,  # 更新时间
            "disable": self.constant.TYPE_INT  # 0:无效 1:有效
        }
