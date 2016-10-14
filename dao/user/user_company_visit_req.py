# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.09
:table user_company_visit_req

"""

from dao.base import BaseDao


class UserCompanyVisitReqDao(BaseDao):

    def __init__(self, logger):
        super(UserCompanyVisitReqDao, self).__init__(logger)
        self.table = 'user_company_visit_req'
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "company_id": self.constant.TYPE_INT,
            "user_id": self.constant.TYPE_INT,

            # 是否申请参观 0：取消申请参观，1：申请参观'
            "status": self.constant.TYPE_INT,
            # 申请参观操作来源 0: 未知，1：微信端，2：PC 端
            "source": self.constant.TYPE_INT,
            # 申请访问时间
            "create_time": self.constant.TYPE_TIMESTAMP,
            # 更新时间
            "update_time": self.constant.TYPE_TIMESTAMP,
        }
