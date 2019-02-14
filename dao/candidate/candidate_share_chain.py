# coding=utf-8

from dao.base import BaseDao


class CandidateShareChainDao(BaseDao):
    def __init__(self):
        super(CandidateShareChainDao, self).__init__()
        self.table = "candidate_share_chain"
        self.fields_map = {
            "id":                  self.constant.TYPE_INT,
            "position_id":         self.constant.TYPE_INT,
            "root_recom_user_id":  self.constant.TYPE_INT,
            "root2_recom_user_id": self.constant.TYPE_INT,
            "recom_user_id":       self.constant.TYPE_INT,
            "presentee_user_id":   self.constant.TYPE_INT,
            "depth":               self.constant.TYPE_INT,
            "type":                self.constant.TYPE_INT,
            "parent_id":           self.constant.TYPE_INT,
            "click_time":          self.constant.TYPE_TIMESTAMP,
            "create_time":         self.constant.TYPE_TIMESTAMP,
            "forward_id":          self.constant.TYPE_STRING,
        }
