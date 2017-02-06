# coding=utf-8

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class CampaignCompanySurveyDao(BaseDao):

    def __init__(self):
        super(CampaignCompanySurveyDao, self).__init__()
        self.table = "campaign_company_survey"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "sysuser_id":   self.constant.TYPE_INT,
            "company_id":   self.constant.TYPE_INT,
            "selected":     self.constant.TYPE_STRING,
            "other":        self.constant.TYPE_STRING,
            "create_time":  self.constant.TYPE_TIMESTAMP
        }
