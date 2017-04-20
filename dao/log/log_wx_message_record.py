# coding=utf-8

from dao.base import BaseDao


class LogWxMessageRecordDao(BaseDao):
    def __init__(self):
        super(LogWxMessageRecordDao, self).__init__()
        self.table = "log_wx_message_record"
        self.fields_map = {
            "id":           self.constant.TYPE_INT,
            "template_id":  self.constant.TYPE_INT,
            "wechat_id":    self.constant.TYPE_INT,
            "msgid":        self.constant.TYPE_INT,
            "open_id":      self.constant.TYPE_STRING,
            "url":          self.constant.TYPE_STRING,
            "topcolor":     self.constant.TYPE_STRING,
            "jsondata":     self.constant.TYPE_STRING,
            "errcode":      self.constant.TYPE_INT,
            "errmsg":       self.constant.TYPE_STRING,
            "sendtime":     self.constant.TYPE_TIMESTAMP,
            "updatetime":   self.constant.TYPE_TIMESTAMP,
            "sendstatus":   self.constant.TYPE_STRING,
            "sendtype":     self.constant.TYPE_INT,
            "access_token": self.constant.TYPE_STRING,
        }
