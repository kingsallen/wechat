# coding=utf-8
# Copyright 2018 MoSeeker

from dao.base import BaseDao


class ReferralRecomHbPositionDao(BaseDao):

    def __init__(self):
        super(ReferralRecomHbPositionDao, self).__init__()
        self.table = 'referral_recom_hb_position'
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "recom_record_id": self.constant.TYPE_INT,
            "hb_item_id":      self.constant.TYPE_INT,
            # 关注时间
            "create_time":     self.constant.TYPE_TIMESTAMP,
            # 更新时间
            "update_time":     self.constant.TYPE_TIMESTAMP,
        }
