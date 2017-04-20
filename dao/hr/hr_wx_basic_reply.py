# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_basic_reply.py
# @DES     : 微信文本回复表

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class HrWxBasicReplyDao(BaseDao):

    def __init__(self):
        super(HrWxBasicReplyDao, self).__init__()
        self.table = "hr_wx_basic_reply"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "rid":             self.constant.TYPE_INT,    # hr_wx_rule.id
            "content":         self.constant.TYPE_STRING, # 文本回复内容
        }
