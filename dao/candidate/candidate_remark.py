# coding=utf-8

from dao.base import BaseDao


class CandidateRemarkDao(BaseDao):
    def __init__(self, logger):
        super(CandidateRemarkDao, self).__init__(logger)
        self.table = "candidate_remark"
        self.fields_map = {
            "id":               self.constant.TYPE_INT,
            "hraccount_id":     self.constant.TYPE_INT,
            "wxuser_id":        self.constant.TYPE_INT,
            "gender":           self.constant.TYPE_INT,
            "age":              self.constant.TYPE_STRING,
            "mobile":           self.constant.TYPE_STRING,
            "email":            self.constant.TYPE_STRING,
            "current_company":  self.constant.TYPE_STRING,
            "current_position": self.constant.TYPE_STRING,
            "education":        self.constant.TYPE_STRING,
            "degree":           self.constant.TYPE_STRING,
            "graduate_at":      self.constant.TYPE_TIMESTAMP,
            "is_star":          self.constant.TYPE_INT,
            "remark":           self.constant.TYPE_STRING,
            "create_time":      self.constant.TYPE_TIMESTAMP,
            "update_time":      self.constant.TYPE_TIMESTAMP,
            "status":           self.constant.TYPE_INT,
            "name":             self.constant.TYPE_STRING
        }
