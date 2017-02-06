# coding=utf-8

from dao.base import BaseDao


class CandidatePositionShareRecordDao(BaseDao):
    def __init__(self):
        super(CandidatePositionShareRecordDao, self).__init__()
        self.table = "candidate_position_share_record"
        self.fields_map = {
            "id":                self.constant.TYPE_INT,
            "wechat_id":         self.constant.TYPE_INT,
            "position_id":       self.constant.TYPE_INT,
            "recom_id":          self.constant.TYPE_INT,
            "recom_user_id":     self.constant.TYPE_INT,
            "viewer_id":         self.constant.TYPE_INT,
            "viewer_ip":         self.constant.TYPE_STRING,
            "source":            self.constant.TYPE_INT,
            "create_time":       self.constant.TYPE_TIMESTAMP,
            "update_time":       self.constant.TYPE_TIMESTAMP,
            "presentee_id":      self.constant.TYPE_INT,
            "click_from":        self.constant.TYPE_INT,
            "presentee_user_id": self.constant.TYPE_INT
        }
