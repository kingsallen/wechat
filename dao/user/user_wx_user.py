# coding=utf-8

from dao.base import BaseDao


class UserWxUserDao(BaseDao):
    def __init__(self):
        super(UserWxUserDao, self).__init__()
        self.table = "user_wx_user"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "wechat_id":       self.constant.TYPE_INT,
            # "group_id":        self.constant.TYPE_INT,
            "sysuser_id":      self.constant.TYPE_INT,
            "is_subscribe":    self.constant.TYPE_INT,
            "openid":          self.constant.TYPE_STRING,
            "nickname":        self.constant.TYPE_STRING,
            "sex":             self.constant.TYPE_INT,
            "city":            self.constant.TYPE_STRING,
            "country":         self.constant.TYPE_STRING,
            "province":        self.constant.TYPE_STRING,
            "language":        self.constant.TYPE_STRING,
            "headimgurl":      self.constant.TYPE_STRING,
            "subscribe_time":  self.constant.TYPE_TIMESTAMP,
            "unsubscibe_time": self.constant.TYPE_TIMESTAMP,
            "unionid":         self.constant.TYPE_STRING,
            # "reward":          self.constant.TYPE_INT,
            # "auto_sync_info":  self.constant.TYPE_INT,
            "create_time":     self.constant.TYPE_TIMESTAMP,
            "update_time":     self.constant.TYPE_TIMESTAMP,
            "source":          self.constant.TYPE_INT
        }
