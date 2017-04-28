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
           {"name":"西安"},
           {"name":"不限"}]

# Cookie name
COOKIE_WELCOME_SEARCH = "SEARCH666"
COOKIE_HRADS_SESSIONS = "HR_ADS"
COOKIE_HRADS_TOTAL = "HR_ADS_TOTAL"

JD_BACKGROUND_IMG = ObjectDict({
    0: ObjectDict({
        "team_img": "11",
        "job_img": "12",
        "company_img": "13",
    }),
    1100: ObjectDict({
        "team_img": "11",
        "job_img": "12",
        "company_img": "13",
    }),
    1200: ObjectDict({
        "team_img": "21",
        "job_img": "22",
        "company_img": "23",
    }),
    1300: ObjectDict({
        "team_img": "31",
        "job_img": "32",
        "company_img": "33",
    }),
    1400: ObjectDict({
        "team_img": "41",
        "job_img": "42",
        "company_img": "43",
    }),
    1500: ObjectDict({
        "team_img": "51",
        "job_img": "52",
        "company_img": "53",
    }),
    1600: ObjectDict({
        "team_img": "61",
        "job_img": "62",
        "company_img": "63",
    }),
    1700: ObjectDict({
        "team_img": "71",
        "job_img": "72",
        "company_img": "73",
    }),
    1800: ObjectDict({
        "team_img": "81",
        "job_img": "82",
        "company_img": "83",
    }),
    1900: ObjectDict({
        "team_img": "91",
        "job_img": "92",
        "company_img": "93",
    }),
    2000: ObjectDict({
        "team_img": "101",
        "job_img": "102",
        "company_img": "103",
    }),
    2100: ObjectDict({
        "team_img": "111",
        "job_img": "112",
        "company_img": "113",
    }),
    2200: ObjectDict({
        "team_img": "121",
        "job_img": "122",
        "company_img": "123",
    }),
})
