# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_hr_chat.py
# @DES     :

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class HrWxHrChatDao(BaseDao):

    def __init__(self):
        super(HrWxHrChatDao, self).__init__()
        self.table = "hr_wx_hr_chat"
        self.fields_map = {
            "id":          self.constant.TYPE_INT,
            "chatlist_id": self.constant.TYPE_INT,
            "content":     self.constant.TYPE_STRING,
            "pid":         self.constant.TYPE_INT,
            "speaker":     self.constant.TYPE_INT,  # 0：求职者，1：HR
            "status":      self.constant.TYPE_INT,  # 0：有效，1：无效
            "create_time": self.constant.TYPE_TIMESTAMP,
        }
