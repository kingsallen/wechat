# coding=utf-8


from dao.base import BaseDao


class HrHbSendRecordDao(BaseDao):
    def __init__(self, logger):
        super(HrHbSendRecordDao, self).__init__(logger)
        self.table = "hr_hb_send_record"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "return_code":  self.constant.TYPE_STRING,
            "return_msg":   self.constant.TYPE_STRING,
            "sign":         self.constant.TYPE_STRING,
            "result_code":  self.constant.TYPE_STRING,
            "err_code":     self.constant.TYPE_STRING,
            "err_code_des": self.constant.TYPE_STRING,
            "mch_billno":   self.constant.TYPE_STRING,
            "mch_id":       self.constant.TYPE_STRING,
            "wxappid":      self.constant.TYPE_STRING,
            "re_openid":    self.constant.TYPE_STRING,
            "total_amount": self.constant.TYPE_INT,
            "send_time":    self.constant.TYPE_STRING,
            "send_listid":  self.constant.TYPE_STRING,
            "create_time":  self.constant.TYPE_TIMESTAMP,
            "hb_item_id":   self.constant.TYPE_INT
        }
