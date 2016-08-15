# coding=utf-8

# Copyright 2016 MoSeeker

'''
:author 潘煜昕（panyuxin@moseeker.com）
:date 2016.07.25
:table hr_company

'''

from dao.base import BaseDao

class HrCompanyDao(BaseDao):

    def __init__(self):
        super(HrCompanyDao, self).__init__()
        self.table = "hr_company"
        self.fields_map = {
            "id": self.constant.TYPE_INT,
            "type": self.constant.TYPE_INT, # 公司区分(其它:2,免费用户:1,企业用户:0)
            "name": self.constant.TYPE_STRING, # 公司注册名称
            "introduction": self.constant.TYPE_STRING, # 企业介绍
            "scale": self.constant.TYPE_INT, # 公司规模
            "address": self.constant.TYPE_STRING, # 企业地址
            "property": self.constant.TYPE_INT, # 公司性质 0:没选择 1:国有 2:三资 3:集体 4:私有
            "industry": self.constant.TYPE_STRING, # 所有行业
            "homepage": self.constant.TYPE_STRING, # 企业网址
            "logo": self.constant.TYPE_STRING, # 企业logo
            "abbreviation": self.constant.TYPE_STRING, # 公司简称
            "impression": self.constant.TYPE_STRING, # json格式的企业印象
            "banner": self.constant.TYPE_STRING, # json格式的企业banner
            "parent_id": self.constant.TYPE_INT, # 上级公司
            "hraccount_id": self.constant.TYPE_INT, # 企业联系人, hr_account.id
            "create_time": self.constant.TYPE_TIMESTAMP, # 创建时间
            "update_time": self.constant.TYPE_TIMESTAMP, # 更新时间
            "disable": self.constant.TYPE_INT, # 0:无效 1:有效
            "source": self.constant.TYPE_INT, # 添加来源 {"0":"hr系统", "9":"profile添加"}'
        }