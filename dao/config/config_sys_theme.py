# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.26
:table config_sys_theme

"""

from dao.base import BaseDao


class ConfigSysThemeDao(BaseDao):

    def __init__(self, logger):
        super(ConfigSysThemeDao, self).__init__(logger)
        self.table = "config_sys_theme"
        self.fields_map = {
            "id":                 self.constant.TYPE_INT,
            "background_color":   self.constant.TYPE_STRING, # 背景色
            "title_color":        self.constant.TYPE_STRING, # 标题
            "button_color":       self.constant.TYPE_STRING, # 按钮
            "other_color":        self.constant.TYPE_STRING, # other
            "free":               self.constant.TYPE_INT, # 是否免费 0：免费 1：收费，只能在大岂后台操作收费主题
            "prority":            self.constant.TYPE_INT, # 排序优先级
            "disable":            self.constant.TYPE_INT, # 是否禁用 0：可用1：不可用
            "create_time":        self.constant.TYPE_TIMESTAMP, # 创建时间
            "update_time":        self.constant.TYPE_TIMESTAMP, # 更新时间
        }
