# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.21
:table hr_media

"""

from dao.base import BaseDao


class HrMediaDao(BaseDao):
    def __init__(self, logger):
        super(HrMediaDao, self).__init__(logger)
        self.table = "hr_media"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "media_url": self.constant.TYPE_STRING,  # 资源链接
            "media_type": self.constant.TYPE_INT,  # 0：image  1: video
            "longtext": self.constant.TYPE_STRING,  # 描述
            "attrs": self.constant.TYPE_STRING,  # 客户属性，可选字段
            "tpl_type": self.constant.TYPE_INT,  # 模板类型1,2,3...对应前端不同template
            "title": self.constant.TYPE_STRING,  # 模板名称
            "sub_title": self.constant.TYPE_STRING,  # 模板子名称
            "link": self.constant.TYPE_STRING,  # 模板链接
        }
