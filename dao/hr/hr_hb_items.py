# coding=utf-8


from dao.base import BaseDao


class HrHbItemsDao(BaseDao):
    def __init__(self):
        super(HrHbItemsDao, self).__init__()
        self.table = "hr_hb_items"
        self.fields_map = {
            "id":                self.constant.TYPE_INT,
            "hb_config_id":      self.constant.TYPE_INT,
            "binding_id":        self.constant.TYPE_INT,
            "index":             self.constant.TYPE_INT,
            "amount":            self.constant.TYPE_FLOAT,
            "status":            self.constant.TYPE_INT,
            "wxuser_id":         self.constant.TYPE_INT,
            "open_time":         self.constant.TYPE_TIMESTAMP,
            "create_time":       self.constant.TYPE_TIMESTAMP,
            "update_time":       self.constant.TYPE_TIMESTAMP,
            "trigger_wxuser_id": self.constant.TYPE_INT
        }
