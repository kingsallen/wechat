# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11,24

 企业主页中模板数据 hr_media 中 id 的 list
 配置中除了 问卷调查survey可以为空外，其余均不可为空，否则影响正常运行。
"""
from util.common import ObjectDict


# DEV1 company setting for moseeker.

COMPANY_4 = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [26, 27, 28, 29, 30],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [39, 40],  # 公司成员
        'events': [35, 36, 37],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})

COMPANY_72 = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [28, 29],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [40],  # 公司成员
        'events': [37],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})


# System testing setting for Mars

COMPANY_MARS_39978 = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [27, 28, 29, 30],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [39, 40],  # 公司成员
        'events': [36, 35, 37],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})

SUB_COMPANY_MARS_40120 = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [30, 27],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [41],  # 公司成员
        'events': [37, 35],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})

SUB_COMPANY_MARS_40627 = ObjectDict({
    'order': ['working_env', 'figure', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [29, 28],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [42],  # 公司成员
        'events': [35, 36],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})


# Product environment company config

COMPANY_MARS = ObjectDict({
    'order': ['working_env', 'figure', 'team', 'members',
              'events', 'address', 'survey'],
    'config': {
        'working_env': [27, 28, 29, 30],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'team': [],  # 团队列表
        'members': [39, 40],  # 公司成员
        'events': [36, 35, 37],  # 公司大事件
        'address': [38],  # 公司地址
        'survey': [],  # 问卷调查
    }
})


# summary config for all companies

COMPANY_CONFIG = ObjectDict({
    '4': COMPANY_4,
    '72': COMPANY_72,
    '39978': COMPANY_MARS_39978,
    '40120': SUB_COMPANY_MARS_40120,
    '40627': SUB_COMPANY_MARS_40627,
})
