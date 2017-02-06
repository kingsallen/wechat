# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_hr_chat_list.py
# @DES     :

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class HrWxHrChatListDao(BaseDao):

    def __init__(self):
        super(HrWxHrChatListDao, self).__init__()
        self.table = "hr_wx_hr_chat_list"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "sysuser_id":      self.constant.TYPE_INT,
            "hraccount_id":    self.constant.TYPE_INT,
            "status":          self.constant.TYPE_INT,
            "create_time":     self.constant.TYPE_TIMESTAMP,
            "wx_chat_time":    self.constant.TYPE_TIMESTAMP,
            "hr_chat_time":    self.constant.TYPE_TIMESTAMP,
        }
