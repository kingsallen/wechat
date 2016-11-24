# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11,24

"""
from util.common import ObjectDict


# 企业主页中模板数据 hr_media 中 id 的 list
SUB_COMPANY = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [],  # 工作环境对应的 hr_media id list
        'figure': [],  # 人物寄语
        'members': [],  # 公司成员
        'events': [],  # 公司大事件
        'address': [],  # 公司地址
        'survey': [],  # 问卷调查
    }
})


COMPANY_CONFIG = ObjectDict({
    'sub_company_1_id': SUB_COMPANY,
    'sub_company_2_id': SUB_COMPANY,
})
