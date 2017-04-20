# coding=utf-8

from dao.base import BaseDao


class CandidateRecomRecordDao(BaseDao):
    def __init__(self):
        super(CandidateRecomRecordDao, self).__init__()
        self.table = "candidate_recom_record"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "position_id":  self.constant.TYPE_INT,
            "app_id":       self.constant.TYPE_INT,
            "presentee_id": self.constant.TYPE_INT,
            "click_time":   self.constant.TYPE_TIMESTAMP,
            "depth":        self.constant.TYPE_INT,
            "recom_id_2":   self.constant.TYPE_INT,
            "recom_id":     self.constant.TYPE_INT,
            "realname":     self.constant.TYPE_STRING,
            "company":      self.constant.TYPE_STRING,
            "position":     self.constant.TYPE_STRING,
            "recom_reason": self.constant.TYPE_STRING,
            "recom_time":   self.constant.TYPE_TIMESTAMP,
            "is_recom":     self.constant.TYPE_INT,
            "create_time":  self.constant.TYPE_TIMESTAMP,
            "update_time":  self.constant.TYPE_TIMESTAMP,
            "mobile":       self.constant.TYPE_STRING,
        }
