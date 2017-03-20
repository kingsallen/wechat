# coding=utf-8

from dao.base import BaseDao


class ConfigSysCvTplDao(BaseDao):
    def __init__(self):
        super(ConfigSysCvTplDao, self).__init__()
        self.table = "config_sys_cv_tpl"
        self.fields_map = {
            "id":                self.constant.TYPE_INT,
            "field_name":        self.constant.TYPE_STRING,
            "field_title":       self.constant.TYPE_STRING,
            "field_type":        self.constant.TYPE_INT,
            "field_value":       self.constant.TYPE_STRING,
            "priority":          self.constant.TYPE_INT,
            "is_basic":          self.constant.TYPE_INT,
            "create_time":       self.constant.TYPE_TIMESTAMP,
            "update_time":       self.constant.TYPE_TIMESTAMP,
            "disable":           self.constant.TYPE_INT,
            "company_id":        self.constant.TYPE_INT,
            "required":          self.constant.TYPE_INT,
            "field_description": self.constant.TYPE_STRING,
            "map":               self.constant.TYPE_STRING
        }
