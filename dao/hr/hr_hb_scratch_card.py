# coding=utf-8


from dao.base import BaseDao


class HrHbScratchCardDao(BaseDao):
    def __init__(self):
        super(HrHbScratchCardDao, self).__init__()
        self.table = "hr_hb_scratch_card"
        self.fields_map = {
            "id":             self.constant.TYPE_INT,
            "wechat_id":      self.constant.TYPE_INT,
            "cardno":         self.constant.TYPE_STRING,
            "status":         self.constant.TYPE_INT,
            "amount":         self.constant.TYPE_FLOAT,
            "hb_config_id":   self.constant.TYPE_INT,
            "bagging_openid": self.constant.TYPE_STRING,
            "create_time":    self.constant.TYPE_TIMESTAMP,
            "hb_item_id":     self.constant.TYPE_INT,
            "tips":           self.constant.TYPE_INT,
        }
