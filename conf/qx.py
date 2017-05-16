# coding=utf-8

# Copyright 2016 MoSeeker

"""
只适合聚合号使用的常量配置

常量使用大写字母，字符串需要时标注为unicode编码
例如 SUCCESS = "成功"

"""

from util.common import ObjectDict

# ++++++++++业务常量+++++++++++
HOTCITY = [{"name":"上海"},
           {"name":"北京"},
           {"name":"深圳"},
           {"name":"广州"},
           {"name":"杭州"},
           {"name":"南京"},
           {"name":"成都"},
           {"name":"苏州"},
           {"name":"武汉"},
           {"name":"天津"},
           {"name":"西安"}]

INDUSTRIES = [
    "计算机/互联网/通信/电子",
    "会计/金融/银行/保险",
    "贸易/消费/制造/营运",
    "制药/医疗",
    # "生产/加工/制造",
    "广告/媒体",
    "房地产/建筑",
    "专业服务/教育/培训",
    "服务业",
    "物流/运输",
    "能源/原材料",
    "政府/非赢利机构/其他"
]

# Cookie name
COOKIE_WELCOME_SEARCH = "SEARCH"
COOKIE_HRADS_SESSIONS = "HR_ADS"
COOKIE_HRADS_TOTAL = "HR_ADS_TOTAL"

JD_BACKGROUND_IMG = ObjectDict({
    0: ObjectDict({
        "team_img": "gamma/industry/0/1.jpg",
        "job_img": "gamma/industry/0/2.jpg",
        "company_img": "gamma/industry/0/3.jpg",
    }),
    1100: ObjectDict({
        "team_img": "gamma/industry/1100/1.jpg",
        "job_img": "gamma/industry/1100/2.jpg",
        "company_img": "gamma/industry/1100/3.jpg",
    }),
    1200: ObjectDict({
        "team_img": "gamma/industry/1200/1.jpg",
        "job_img": "gamma/industry/1200/2.jpg",
        "company_img": "gamma/industry/1200/3.jpg",
    }),
    1300: ObjectDict({
        "team_img": "gamma/industry/1300/1.jpg",
        "job_img": "gamma/industry/1300/2.jpg",
        "company_img": "gamma/industry/1300/3.jpg",
    }),
    1400: ObjectDict({
        "team_img": "gamma/industry/1400/1.jpg",
        "job_img": "gamma/industry/1400/2.jpg",
        "company_img": "gamma/industry/1400/3.jpg",
    }),
    1500: ObjectDict({
        "team_img": "gamma/industry/1500/1.jpg",
        "job_img": "gamma/industry/1500/2.jpg",
        "company_img": "gamma/industry/1500/3.jpg",
    }),
    1600: ObjectDict({
        "team_img": "gamma/industry/1600/1.jpg",
        "job_img": "gamma/industry/1600/2.jpg",
        "company_img": "gamma/industry/1600/3.jpg",
    }),
    1700: ObjectDict({
        "team_img": "gamma/industry/1700/1.jpg",
        "job_img": "gamma/industry/1700/2.jpg",
        "company_img": "gamma/industry/1700/3.jpg",
    }),
    1800: ObjectDict({
        "team_img": "gamma/industry/1800/1.jpg",
        "job_img": "gamma/industry/1800/2.jpg",
        "company_img": "gamma/industry/1800/3.jpg",
    }),
    1900: ObjectDict({
        "team_img": "gamma/industry/1900/1.jpg",
        "job_img": "gamma/industry/1900/2.jpg",
        "company_img": "gamma/industry/1900/3.jpg",
    }),
    2000: ObjectDict({
        "team_img": "gamma/industry/2000/1.jpg",
        "job_img": "gamma/industry/2000/2.jpg",
        "company_img": "gamma/industry/2000/3.jpg",
    }),
    2100: ObjectDict({
        "team_img": "gamma/industry/2100/1.jpg",
        "job_img": "gamma/industry/2100/2.jpg",
        "company_img": "gamma/industry/2100/3.jpg",
    }),
    2200: ObjectDict({
        "team_img": "gamma/industry/2200/1.jpg",
        "job_img": "gamma/industry/2200/2.jpg",
        "company_img": "gamma/industry/2200/3.jpg",
    }),
})
