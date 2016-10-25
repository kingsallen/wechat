# coding=utf-8


from dao.base import BaseDao


class HrHbPositionBindingDao(BaseDao):
    def __init__(self, logger):
        super(HrHbPositionBindingDao, self).__init__(logger)
        self.table = "hr_hb_position_binding"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "hb_config_id": self.constant.TYPE_INT,
            "position_id":  self.constant.TYPE_INT,
            "trigger_way":  self.constant.TYPE_INT,
            "total_amount": self.constant.TYPE_FLOAT,
            "total_num":    self.constant.TYPE_INT,
            "create_time":  self.constant.TYPE_TIMESTAMP,
            "update_time":  self.constant.TYPE_TIMESTAMP
        }
