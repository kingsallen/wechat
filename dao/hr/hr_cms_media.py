# -*- coding=utf-8 -*-
# Copyright 2017 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2017.03.27
:table hr_cms_media

"""

from dao.base import BaseDao


class HrCmsMediaDao(BaseDao):
    def __init__(self, logger):
        super(HrCmsMediaDao, self).__init__(logger)
        self.table = "hr_cms_media"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "module_id": self.constant.TYPE_INT,
            "longtexts": self.constant.TYPE_STRING,  # 描述
            "attrs": self.constant.TYPE_STRING,  # 扩展字段, eg, 地图存json
            "title": self.constant.TYPE_STRING,  # 标题
            "sub_title": self.constant.TYPE_STRING,  # 副标题
            "link": self.constant.TYPE_STRING,  # 链接
            "res_id": self.constant.TYPE_INT,  # 资源 hr_resource.id
            "orders": self.constant.TYPE_INT,  # 顺序
            "is_show": self.constant.TYPE_INT,  # 是否展示
            "disable": self.constant.TYPE_INT,  # 0:无效 1:有效
            "create_time": self.constant.TYPE_TIMESTAMP,  # 创建时间
            "update_time": self.constant.TYPE_TIMESTAMP,  # 更新时间
        }
