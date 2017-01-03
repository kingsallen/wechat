# coding=utf-8

from dao.base import BaseDao


class JobApplicationDao(BaseDao):

    def __init__(self, logger):
        super(JobApplicationDao, self).__init__(logger)
        self.table = "job_application"
        self.fields_map = {
            "id":               self.constant.TYPE_INT,
            "wechat_id":        self.constant.TYPE_INT,
            "position_id":      self.constant.TYPE_INT,
            "recommender_id":   self.constant.TYPE_INT,
            "submit_time":      self.constant.TYPE_TIMESTAMP,
            "status_id":        self.constant.TYPE_INT,
            "l_application_id": self.constant.TYPE_INT,
            "reward":           self.constant.TYPE_INT,
            "source_id":        self.constant.TYPE_INT,
            "_create_time":     self.constant.TYPE_TIMESTAMP,
            "applier_id":       self.constant.TYPE_INT,
            "interview_id":     self.constant.TYPE_INT,
            # "resume_id":        self.constant.TYPE_STRING, 旧时代的产物，已废
            "ats_status":       self.constant.TYPE_INT,
            "applier_name":     self.constant.TYPE_STRING,
            "disable":          self.constant.TYPE_INT,
            "routine":          self.constant.TYPE_INT,
            "is_viewed":        self.constant.TYPE_INT,
            "not_suitable":     self.constant.TYPE_INT,
            "company_id":       self.constant.TYPE_INT,
            "update_time":      self.constant.TYPE_TIMESTAMP,
            "app_tpl_id":       self.constant.TYPE_INT,
            "proxy":            self.constant.TYPE_INT,
            "apply_type":       self.constant.TYPE_INT,
            "email_status":     self.constant.TYPE_INT,
            "view_count":       self.constant.TYPE_INT,
        }
