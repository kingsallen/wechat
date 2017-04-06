# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.12.20
:table hr_resource

"""

from dao.base import BaseDao


class HrResourceDao(BaseDao):
    def __init__(self, logger):
        super(HrResourceDao, self).__init__(logger)
        self.table = "hr_resource"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "res_url": self.constant.TYPE_STRING,  # 资源链接
            "res_type": self.constant.TYPE_INT,  # 资源类型 0: image, 1: video
            "remark": self.constant.TYPE_STRING,  # 资源备注，方便调用者识别资源
            "disable": self.constant.TYPE_INT,  # 0:无效 1:有效
            "company_id": self.constant.TYPE_INT,  # hr_company.id
            "title": self.constant.TYPE_STRING,  # 资源名称
            "cover": self.constant.TYPE_STRING,  # 视频封面
        }
