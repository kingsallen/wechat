# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11,24

 企业主页中模板数据 hr_media 中 id 的 list
 配置中除了 问卷调查survey, qr_code可以为空外，其余均不可为空，否则影响正常运行。
"""
from util.common import ObjectDict

# DEV1 company setting for moseeker.

COMPANY_72 = ObjectDict({
    'order': ['working_env', 'figure', 'team', 'members',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [28, 29],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [40],  # 公司成员
        'events': [37],  # 公司大事件
        'map': [38],  # 公司地址
        'survey': [],  # 问卷调查
        'qr_code': []  # 二维码
    },
})

# System testing setting for Mars

COMPANY_MARS_39978 = ObjectDict({
    'order': ['working_env', 'figure', 'team', 'members',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [41, 44, 42, 45, 43, 46],  # 工作环境对应的 hr_media id list
        'figure': [47],  # 人物寄语
        'team': [48],  # 团队列表
        'members': [49],  # 公司成员
        'events': [50, 51, 52],  # 公司大事件
        'map': [53],  # 公司地址
        'survey': [],  # 问卷调查
        'qr_code': [175]  # 二维码
    },
    'no_jd_team': True,
    'custom_visit_recipe': ['火星参观活动暂未开通', '请耐心等待哦~'],
    'transfer': {
        'cm': '关注玛氏中国，开启一段全新的旅程。',  # company main page
        'tl': '玛氏中国团队，一起奋斗未来的地方。',  # team list page
        'td': '“加入我们”之前，先来了解我们的团队职能、发展机会和团队风格。'  # team detail page
    }
})

SUB_COMPANY_MARS_40120 = ObjectDict({
    'order': ['working_env', 'figure', 'team', 'members',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [30, 27],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [41],  # 公司成员
        'events': [37, 35],  # 公司大事件
        'map': [38],  # 公司地址
        'survey': [],  # 问卷调查
        'qr_code': []  # 二维码
    }
})

# Product environment company config

COMPANY_MOSEEKER = ObjectDict({
    'order': ['working_env', 'figure', 'team', 'members',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [26, 27, 28, 29, 30],  # 工作环境对应的 hr_media id list
        'figure': [31],  # 人物寄语
        'members': [39, 40],  # 公司成员
        'events': [35, 36, 37],  # 公司大事件
        'map': [38],  # 公司地址
        'survey': [],  # 问卷调查
        'qr_code': []  # 二维码
    }
})

COMPANY_MARS = ObjectDict({
    'order': ['working_env', 'figure', 'team', 'members',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [41, 44, 42, 45, 43, 46],  # 工作环境对应的 hr_media id list
        'figure': [47],  # 人物寄语
        'team': [48],  # 团队列表
        'members': [49],  # 公司成员
        'events': [50, 51, 52],  # 公司大事件
        'map': [53],  # 公司地址
        'survey': [],  # 问卷调查
        'qr_code': [175]  # 二维码
    },
    'no_jd_team': True,
    'custom_visit_recipe': ['火星参观活动暂未开通', '请耐心等待哦~'],
    'transfer': {
        'cm': '关注玛氏中国，开启一段全新的旅程。',  # company main page
        'tl': '玛氏中国团队，一起奋斗未来的地方。',  # team list page
        'td': '“加入我们”之前，先来了解我们的团队职能、发展机会和团队风格。'  # team detail page
    }
})

COMPANY_OSRAM = ObjectDict({
    'order': ['figure', 'team', 'members', 'working_env',
              'events', 'address', 'survey', 'qr_code'],
    'config': {
        'working_env': [120, 121, 122, 123],  # 工作环境对应的 hr_media id list
        'figure': [114],  # 人物寄语
        'members': [115, 116, 117, 118, 119],  # 公司成员
        'events': [124, 125, 126],  # 公司大事件
        'address': [127, 176, 128, 129, 130, 131],  # 公司地址
        'survey': [],  # 问卷调查
        'qr_code': [132]  # 二维码
    },
})

COMPANY_NET_EASE = ObjectDict({
    'order': ['working_env', 'members', 'team',
              'events', 'survey', 'qr_code'],
    'config': {
        'working_env': [179, 180, 181, 182, 183, 184],  # 工作环境对应的 hr_media id list
        'members': [185],  # 公司成员
        'events': [192, 193, 194],  # 公司大事件
        'survey': [],  # 问卷调查
        'qr_code': [195]  # 二维码
    },
})

COMPANY_JOHNSON = ObjectDict({
    'order': ['working_env', 'figure', 'members', 'team',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [263, 264, 265, 266, 267, 268],  # 工作环境对应的 hr_media id list
        'figure': [269],  # 人物寄语
        'members': [270],  # 我们的愿景
        'events': [271, 272, 273],  # 公司大事件
        'map': [279],  # 公司地图
        'survey': [],  # 问卷调查
        'qr_code': [274]  # 二维码
    },
})

COMPANY_MONDELEZ = ObjectDict({
    'order': ['working_env', 'figure', 'team',
              'events', 'map', 'survey', 'qr_code'],
    'config': {
        'working_env': [293, 292, 280],  # 公司文化 hr_media id list
        'figure': [291],  # 人物寄语
        'events': [281, 282, 283],  # 公司大事件
        'map': [294],  # 公司地图
        'survey': [],  # 问卷调查
        'qr_code': [295]  # 二维码
    },
})

COMPANY_ACTIONSKY = ObjectDict({
    'order': ['working_env', 'members', 'team',
              'events', 'address', 'survey', 'qr_code'],
    'config': {
        'working_env': [296, 297, 298, 299, 300],  # 工作环境对应的 hr_media id list
        # 'figure': [],  # 人物寄语
        'members': [301, 302],  # 成员采访
        'events': [305, 304, 303],  # 公司大事件
        'address': [306],  # 公司地图
        'survey': [],  # 问卷调查
        'qr_code': [307]  # 二维码
    },
})

COMPANY_BLUEFOCUS = ObjectDict({
    'order': ['figure', 'team', 'members', 'working_env',
              'events', 'survey', 'qr_code'],
    'config': {
        'figure': [310],  # 人物寄语
        'team': [354],
        'members': [311],  # 成员采访
        'working_env': [312, 313, 314, 315, 316, 317],  # 工作环境对应的 hr_media id list
        'events': [318, 319, 320],  # 公司大事件
        # 'address': [306],  # 公司地图
        'survey': [],  # 问卷调查
        'qr_code': [321]  # 二维码
    },
})

# summary config for all companies

COMPANY_CONFIG = ObjectDict({
    # 测试调试配置
    # 72: COMPANY_72,
    4: COMPANY_BLUEFOCUS,
    39978: COMPANY_BLUEFOCUS,
    # 39979: COMPANY_72,
    # 40120: SUB_COMPANY_MARS_40120,

    # 线上配置
    650: COMPANY_MOSEEKER,
    27: COMPANY_OSRAM,
    91572: COMPANY_MARS,
    1424: COMPANY_NET_EASE,
    102566: COMPANY_JOHNSON,
    157: COMPANY_MONDELEZ,
    87954: COMPANY_ACTIONSKY,
    52813: COMPANY_BLUEFOCUS
})
