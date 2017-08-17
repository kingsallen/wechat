# coding=utf-8

from dao.base import BaseDao


class ProfileOtherDao(BaseDao):
    def __init__(self):
        super(ProfileOtherDao, self).__init__()
        self.table = "profile_other"
        self.fields_map = {
            "profile_id":  self.constant.TYPE_INT,
            "other":       self.constant.TYPE_STRING,
            "create_time": self.constant.TYPE_TIMESTAMP,
            "update_time": self.constant.TYPE_TIMESTAMP
        }
