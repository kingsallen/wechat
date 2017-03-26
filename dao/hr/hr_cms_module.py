# -*- coding=utf-8 -*-
# Copyright 2017 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2017.03.27
:table hr_cms_media

"""

from dao.base import BaseDao


class HrCmsModuleDao(BaseDao):
    def __init__(self, logger):
        super(HrCmsModuleDao, self).__init__(logger)
        self.table = "hr_cms_module"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "page_id": self.constant.TYPE_INT,  # hr_cms_pages.id
            "module_name": self.constant.TYPE_STRING,  # 模块名称
            "type": self.constant.TYPE_INT,  # 模块类型
            "orders": self.constant.TYPE_INT,  # 顺序
            "link": self.constant.TYPE_STRING,  # 模板链接
            "limit": self.constant.TYPE_INT,  # 显示限制
            "disable": self.constant.TYPE_INT,  # 0:无效 1:有效
            "create_time": self.constant.TYPE_TIMESTAMP,  # 创建时间
            "update_time": self.constant.TYPE_TIMESTAMP,  # 更新时间
        }
