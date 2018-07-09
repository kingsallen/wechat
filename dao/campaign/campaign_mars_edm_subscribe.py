# coding=utf-8

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class CampaignMarsEdmSubscribeDao(BaseDao):

    def __init__(self):
        super(CampaignMarsEdmSubscribeDao, self).__init__()
        self.table = "campaign_mars_edm_subscribe"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "name":         self.constant.TYPE_STRING,
            "mobile":       self.constant.TYPE_INT,
            "email":        self.constant.TYPE_STRING,
            "wxuser_id":    self.constant.TYPE_INT,
            "update_time":  self.constant.TYPE_TIMESTAMP,
            "create_time":  self.constant.TYPE_TIMESTAMP
        }
