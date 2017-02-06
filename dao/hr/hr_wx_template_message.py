# coding=utf-8

from dao.base import BaseDao


class HrWxTemplateMessageDao(BaseDao):
    def __init__(self):
        super(HrWxTemplateMessageDao, self).__init__()
        self.table = "hr_wx_template_message"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "sys_template_id": self.constant.TYPE_INT,
            "wx_template_id":  self.constant.TYPE_STRING,
            "display":         self.constant.TYPE_INT,
            "priority":        self.constant.TYPE_INT,
            "wechat_id":       self.constant.TYPE_INT,
            "disable":         self.constant.TYPE_INT,
            "url":             self.constant.TYPE_STRING,
            "topcolor":        self.constant.TYPE_STRING,
            "first":           self.constant.TYPE_STRING,
            "remark":          self.constant.TYPE_STRING,
        }
