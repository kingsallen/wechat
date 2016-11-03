# coding=utf-8

# @Time    : 10/28/16 09:58
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_points_conf.py
# @DES     :

# Copyright 2016 MoSeeker

from dao.base import BaseDao

class HrPointsConfDao(BaseDao):
    def __init__(self, logger):
        super(HrPointsConfDao, self).__init__(logger)
        self.table = "hr_points_conf"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "company_id":      self.constant.TYPE_INT,
            "status_name":     self.constant.TYPE_STRING,
            "reward":          self.constant.TYPE_INT,
            "description":     self.constant.TYPE_STRING,
            "is_using":        self.constant.TYPE_INT,
            "order_num":       self.constant.TYPE_INT,
            "_update_time":    self.constant.TYPE_TIMESTAMP,
            "tag":             self.constant.TYPE_STRING,
            "is_applier_send": self.constant.TYPE_INT,
            "applier_first":   self.constant.TYPE_STRING,
            "applier_remark":  self.constant.TYPE_STRING,
            "is_recom_send":   self.constant.TYPE_INT,
            "recom_first":     self.constant.TYPE_STRING,
            "recom_remark":    self.constant.TYPE_STRING,
            "template_id":     self.constant.TYPE_INT,
        }
