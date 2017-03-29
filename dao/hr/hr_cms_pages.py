# coding=utf-8

# Copyright 2017 MoSeeker

"""
:author 陈迪（panyuxin@moseeker.com）
:date 2017.03.26
:table hr_cms_pages

"""

from dao.base import BaseDao

class HrCmsPagesDao(BaseDao):

    def __init__(self, logger):
        super(HrCmsPagesDao, self).__init__(logger)
        self.table = "hr_cms_pages"
        self.fields_map = {
            "id":             self.constant.TYPE_INT,
            "config_id":      self.constant.TYPE_INT,  # company_id/team_id
            "type":           self.constant.TYPE_INT,  # 页面类型, 1为企业首页(config_id为company_id)2，团队详情（config_id为team_id） ，3，详情职位详情(config_id为team_id)
            "disable":        self.constant.TYPE_INT,  # 0:无效 1:有效
            "create_time":    self.constant.TYPE_TIMESTAMP,  # 创建时间
            "update_time":    self.constant.TYPE_TIMESTAMP,  # 更新时间
        }
