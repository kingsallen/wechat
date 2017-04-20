# coding=utf-8

from dao.base import BaseDao


class UserHrAccountDao(BaseDao):
    def __init__(self):
        super(UserHrAccountDao, self).__init__()
        self.table = "user_hr_account"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "company_id":      self.constant.TYPE_INT,
            "mobile":          self.constant.TYPE_STRING,
            "email":           self.constant.TYPE_STRING,
            "wxuser_id":       self.constant.TYPE_INT,
            "password":        self.constant.TYPE_STRING,
            "username":        self.constant.TYPE_STRING,
            "account_type":    self.constant.TYPE_INT,
            "activation":      self.constant.TYPE_INT,
            "disable":         self.constant.TYPE_INT,
            "register_time":   self.constant.TYPE_TIMESTAMP,
            "register_ip":     self.constant.TYPE_STRING,
            "last_login_time": self.constant.TYPE_TIMESTAMP,
            "last_login_ip":   self.constant.TYPE_STRING,
            "login_count":     self.constant.TYPE_INT,
            "source":          self.constant.TYPE_INT,
            "download_token":  self.constant.TYPE_STRING,
            "create_time":     self.constant.TYPE_TIMESTAMP,
            "update_time":     self.constant.TYPE_TIMESTAMP,
            "headimgurl":      self.constant.TYPE_STRING,
        }
