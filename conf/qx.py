# coding=utf-8

# Copyright 2016 MoSeeker

"""
只适合聚合号使用的常量配置

常量使用大写字母，字符串需要时标注为unicode编码
例如 SUCCESS = "成功"

"""

from util.common import ObjectDict

# ++++++++++业务常量+++++++++++
hot_city = ObjectDict({
    "hot_city": ['上海','北京','深圳','广州','杭州',
                 '南京','成都','苏州','武汉','天津',
                 '西安','不限']
})

# Cookie name
COOKIE_WELCOME_SEARCH = "SEARCH666"
COOKIE_HRADS_SESSIONS = "HR_ADS"
COOKIE_HRADS_TOTAL = "HR_ADS_TOTAL"
