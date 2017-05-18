# coding=utf-8

# @Time    : 10/26/16 18:15
# @Author  : panda (panyuxin@moseeker.com)
# @File    : job_position_ext.py
# @DES     : 职位副表

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class JobPositionExtDao(BaseDao):

    def __init__(self):
        super(JobPositionExtDao, self).__init__()
        self.table = "job_position_ext"
        self.fields_map = {
            "pid":            self.constant.TYPE_INT,
            "job_custom_id":  self.constant.TYPE_INT,
            "job_occupation_id": self.constant.TYPE_INT,
            "update_time":    self.constant.TYPE_TIMESTAMP,
            "create_time":    self.constant.TYPE_TIMESTAMP,
        }
