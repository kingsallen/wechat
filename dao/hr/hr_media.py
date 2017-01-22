# coding=utf-8
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
            "res_id": self.constant.TYPE_INT,  # 资源 hr_resource.id
            "longtext": self.constant.TYPE_STRING,  # 描述
            "attrs": self.constant.TYPE_STRING,  # 客户属性，可选字段
            "title": self.constant.TYPE_STRING,  # 模板名称
            "sub_title": self.constant.TYPE_STRING,  # 模板子名称
            "link": self.constant.TYPE_STRING,  # 模板链接
        }
