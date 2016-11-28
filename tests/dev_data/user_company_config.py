# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11,24

"""
from util.common import ObjectDict


# 企业主页中模板数据 hr_media 中 id 的 list


COMPANY_4 = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [26, 27, 28, 29, 30],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [32, 33, 34],  # 公司成员
        'events': [35, 36, 37],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})


COMPANY_CONFIG = ObjectDict({
    '4': COMPANY_4,
    # 'sub_company_2_id': SUB_COMPANY,
})
