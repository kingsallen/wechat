# coding=utf-8

# @Time    : 10/27/16 10:12
# @Author  : panda (panyuxin@moseeker.com)
# @File    : hr_company_account.py
# @DES     : 公司和 HR帐号关系表

# Copyright 2016 MoSeeker

from dao.base import BaseDao

class HrCompanyAccountDao(BaseDao):

    def __init__(self):

        super(HrCompanyAccountDao, self).__init__()
        self.table = "hr_company_account"
        self.fields_map = {
            "company_id": self.constant.TYPE_INT,
            "account_id": self.constant.TYPE_INT,
        }
