# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.25
:table job_occupation

"""

from dao.base import BaseDao


class JobOccupationDao(BaseDao):

    def __init__(self, logger):
        super(JobOccupationDao, self).__init__(logger)
        self.table = "job_occupation"
        self.fields_map = {
            "id":             self.constant.TYPE_INT,
            "company_id":     self.constant.TYPE_INT, # hr_company.id
            "status":         self.constant.TYPE_INT, # 职位自定义字段是否有效，0：无效；1：有效
            "name":           self.constant.TYPE_STRING, # 自定义职能名称
            "create_time":    self.constant.TYPE_TIMESTAMP, # 创建时间
            "update_time":    self.constant.TYPE_TIMESTAMP, # 更新时间
        }
