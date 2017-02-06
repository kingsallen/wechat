# coding=utf-8

from dao.base import BaseDao


class JobPositionShareTplConfDao(BaseDao):

    def __init__(self):
        super(JobPositionShareTplConfDao, self).__init__()
        self.table = "job_position_share_tpl_conf"
        self.fields_map = {
            "id":          self.constant.TYPE_INT,
            "type":        self.constant.TYPE_INT,
            "name":        self.constant.TYPE_STRING,
            "title":       self.constant.TYPE_STRING,
            "description": self.constant.TYPE_STRING,
            "disable":     self.constant.TYPE_INT,
            "remark":      self.constant.TYPE_STRING,
            "priority":    self.constant.TYPE_INT
        }
