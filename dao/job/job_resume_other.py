# coding=utf-8

from dao.base import BaseDao


class JobResumeOtherDao(BaseDao):
    def __init__(self):
        super(JobResumeOtherDao, self).__init__()
        self.table = "job_resume_other"
        self.fields_map = {
            "app_id":      self.constant.TYPE_INT,
            "other":       self.constant.TYPE_STRING,
            "create_time": self.constant.TYPE_TIMESTAMP,
            "update_time": self.constant.TYPE_TIMESTAMP
        }
