# coding=utf-8

from dao.base import BaseDao


class LogDatagroupPrepareDataDao(BaseDao):
    def __init__(self):
        super(LogDatagroupPrepareDataDao, self).__init__()
        self.table = "log_datagroup_prepare_data"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "flag":         self.constant.TYPE_INT,
            "wechat_id":    self.constant.TYPE_INT,
            "wxuser_id":    self.constant.TYPE_INT,
            "create_time":  self.constant.TYPE_TIMESTAMP,
            "update_time":   self.constant.TYPE_TIMESTAMP,
        }
