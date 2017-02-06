# coding=utf-8

from dao.base import BaseDao


class UserEmployeeDao(BaseDao):
    def __init__(self):
        super(UserEmployeeDao, self).__init__()
        self.table = "user_employee"
        self.fields_map = {
            "id":                 self.constant.TYPE_INT,
            "employeeid":         self.constant.TYPE_STRING,
            "company_id":         self.constant.TYPE_INT,
            # "role_id":            self.constant.TYPE_INT,
            "wxuser_id":          self.constant.TYPE_INT,
            # "sex":                self.constant.TYPE_INT,
            "ename":              self.constant.TYPE_STRING,
            "efname":             self.constant.TYPE_STRING,
            "cname":              self.constant.TYPE_STRING,
            "cfname":             self.constant.TYPE_STRING,
            # "password":           self.constant.TYPE_STRING,
            # "is_admin":           self.constant.TYPE_INT,
            "status":             self.constant.TYPE_INT,
            "companybody":        self.constant.TYPE_STRING,
            "departmentname":     self.constant.TYPE_STRING,
            # "groupname":          self.constant.TYPE_STRING,
            # "position":           self.constant.TYPE_STRING,
            # "employdate":         self.constant.TYPE_TIMESTAMP,
            # "managername":        self.constant.TYPE_STRING,
            # "city":               self.constant.TYPE_STRING,
            # "birthday":           self.constant.TYPE_TIMESTAMP,
            # "retiredate":         self.constant.TYPE_TIMESTAMP,
            # "education":          self.constant.TYPE_STRING,
            # "address":            self.constant.TYPE_STRING,
            # "idcard":             self.constant.TYPE_STRING,
            "mobile":             self.constant.TYPE_STRING,
            "award":              self.constant.TYPE_INT,
            "binding_time":       self.constant.TYPE_TIMESTAMP,
            "email":              self.constant.TYPE_STRING,
            "activation":         self.constant.TYPE_INT,
            "activation_code":    self.constant.TYPE_STRING,
            "disable":            self.constant.TYPE_INT,
            "create_time":        self.constant.TYPE_TIMESTAMP,
            "update_time":        self.constant.TYPE_TIMESTAMP,
            # "auth_level":         self.constant.TYPE_INT,
            "register_time":      self.constant.TYPE_TIMESTAMP,
            "register_ip":        self.constant.TYPE_STRING,
            # "last_login_time":    self.constant.TYPE_TIMESTAMP,
            # "last_login_ip":      self.constant.TYPE_STRING,
            # "login_count":        self.constant.TYPE_INT,
            "source":             self.constant.TYPE_INT,
            # "download_token":     self.constant.TYPE_STRING,
            # "hr_wxuser_id":       self.constant.TYPE_INT,
            "custom_field":       self.constant.TYPE_STRING,
            "is_rp_sent":         self.constant.TYPE_INT,
            "sysuser_id":         self.constant.TYPE_INT,
            "position_id":        self.constant.TYPE_INT,
            "section_id":         self.constant.TYPE_INT,
            "email_isvalid":      self.constant.TYPE_INT,
            "auth_method":        self.constant.TYPE_INT,
            "custom_field_values":self.constant.TYPE_STRING
        }
