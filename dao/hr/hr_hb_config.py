# coding=utf-8


from dao.base import BaseDao


class HrHbConfigDao(BaseDao):
    def __init__(self):
        super(HrHbConfigDao, self).__init__()
        self.table = "hr_hb_config"
        self.fields_map = {
            "id":               self.constant.TYPE_INT,
            "type":             self.constant.TYPE_INT,
            "target":           self.constant.TYPE_INT,
            "company_id":       self.constant.TYPE_INT,
            "start_time":       self.constant.TYPE_TIMESTAMP,
            "end_time":         self.constant.TYPE_TIMESTAMP,
            "total_amount":     self.constant.TYPE_FLOAT,
            "range_min":        self.constant.TYPE_FLOAT,
            "range_max":        self.constant.TYPE_FLOAT,
            "probability":      self.constant.TYPE_FLOAT,
            "d_type":           self.constant.TYPE_INT,
            "headline":         self.constant.TYPE_STRING,
            "headline_failure": self.constant.TYPE_STRING,
            "share_title":      self.constant.TYPE_STRING,
            "share_desc":       self.constant.TYPE_STRING,
            "share_img":        self.constant.TYPE_STRING,
            "status":           self.constant.TYPE_INT,
            "checked":          self.constant.TYPE_INT,
            "estimated_total":  self.constant.TYPE_INT,
            "create_time":      self.constant.TYPE_TIMESTAMP,
            "update_time":      self.constant.TYPE_TIMESTAMP,
            "actual_total":     self.constant.TYPE_INT
        }
