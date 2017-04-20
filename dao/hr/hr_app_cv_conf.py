# coding=utf-8

# @Time    : 10/28/16 09:58
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_app_cv_conf.py
# @DES     : 企业申请简历校验配置


from dao.base import BaseDao

class HrAppCvConfDao(BaseDao):
    def __init__(self):
        super(HrAppCvConfDao, self).__init__()
        self.table = "hr_app_cv_conf"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "name":            self.constant.TYPE_STRING,
            "priority":        self.constant.TYPE_INT,
            "disable":         self.constant.TYPE_INT,
            "company_id":      self.constant.TYPE_INT,
            "hraccount_id":    self.constant.TYPE_INT,
            "required":        self.constant.TYPE_INT,
            "field_value":     self.constant.TYPE_STRING,
            "create_time":     self.constant.TYPE_TIMESTAMP,
            "update_time":     self.constant.TYPE_TIMESTAMP,
        }
