# coding=utf-8

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class UserEmployeePointsRecordDao(BaseDao):
    def __init__(self, logger):
        super(UserEmployeePointsRecordDao, self).__init__(logger)
        self.table = "user_employee_points_record"
        self.fields_map = {
            'id':                self.constant.TYPE_INT,
            'employee_id':       self.constant.TYPE_INT,
            'reason':            self.constant.TYPE_STRING,
            'award':             self.constant.TYPE_INT,
            '_create_time':      self.constant.TYPE_TIMESTAMP,
            'application_id':    self.constant.TYPE_INT,
            'recom_wxuser':      self.constant.TYPE_INT,
            'update_time':       self.constant.TYPE_TIMESTAMP,
            'position_id':       self.constant.TYPE_INT,
            'berecom_wxuser_id': self.constant.TYPE_INT,
            'award_config_id':   self.constant.TYPE_INT,
            'recom_user_id':     self.constant.TYPE_INT,
            'berecom_user_id':   self.constant.TYPE_INT
        }
