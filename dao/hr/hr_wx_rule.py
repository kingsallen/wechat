# coding=utf-8

# @Time    : 10/27/16 12:13
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_wx_rule.py
# @DES     : 微信回复规则表

# Copyright 2016 MoSeeker

from dao.base import BaseDao


class HrWxRuleDao(BaseDao):

    def __init__(self):
        super(HrWxRuleDao, self).__init__()
        self.table = "hr_wx_rule"
        self.fields_map = {
            "id":              self.constant.TYPE_INT,
            "wechat_id":       self.constant.TYPE_INT,
            "cid":             self.constant.TYPE_INT,
            "name":            self.constant.TYPE_STRING,  # 规则名称
            "module":          self.constant.TYPE_STRING,  # 模块名称
            "displayorder":    self.constant.TYPE_INT,     # 排序
            "status":          self.constant.TYPE_INT,     # 规则状态，0禁用，1启用，2置顶
            "access_level":    self.constant.TYPE_INT,     # 规则获取权限，0：所有，1：员
            "keywords":        self.constant.TYPE_STRING,  # 关键字
        }
