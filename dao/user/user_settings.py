# coding=utf-8

from dao.base import BaseDao


class UserSettingsDao(BaseDao):
    def __init__(self, logger):
        super(UserSettingsDao, self).__init__(logger)
        self.table = "user_settings"
        self.fields_map = {
            "id":             self.constant.TYPE_INT,
            "user_id":        self.constant.TYPE_INT,
            "banner_url":     self.constant.TYPE_STRING,
            "privacy_policy": self.constant.TYPE_INT
        }
