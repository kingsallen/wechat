# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_basic_reply.py
# @DES     : 微信图文回复表

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class HrWxBasicReplyDao(BaseDao):

    def __init__(self):
        super(HrWxBasicReplyDao, self).__init__()
        self.table = "hr_wx_basic_reply"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "rid":             self.constant.TYPE_INT,
            "parentid":        self.constant.TYPE_INT,
            "title":           self.constant.TYPE_STRING,
            "description":     self.constant.TYPE_STRING,
            "thumb":           self.constant.TYPE_STRING,
            "content":         self.constant.TYPE_STRING,
            "url":             self.constant.TYPE_STRING,
        }
