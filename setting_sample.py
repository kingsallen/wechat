# coding=utf-8

# Copyright 2016 MoSeeker

"""
说明:
setting配置常量规范：
1.常量适用于整个系统，偏系统设置，如数据库配置、服务器路径等
2.常量不涉及具体业务逻辑（业务逻辑常量配置在constant.py中）
3.尽量考虑复用性
"""

import os
from util.common import ObjectDict
from tornado.options import define

define("port", default=8000, help="run on the given port", type=int)
define("logpath", default="logs/", help="log path")
define("env", default="platform", help="wechat product")

settings = ObjectDict()
settings['xsrf_cookies'] = True
settings['cookie_secret'] = "EAB1D2AB05EEF04D35BA5FDF789DD6A3"
settings['debug'] = True
settings['log_level'] = "DEBUG"
settings['static_domain'] = "//static1.dqprism.com"
# 和前端工程师远程调试时可以开启此项,并配置remote_debug_ip选项
settings['remote_debug'] = False
# 远程/本地 前端build服务器地址
settings['remote_debug_ip'] = 'http://0.0.0.0:3003'

settings['root_path'] = os.path.join(os.path.dirname(__file__), "")
settings['template_path'] = os.path.join(settings['root_path'], "template")
settings['static_path'] = os.path.join(settings['root_path'], "static")
settings['static_upload_path'] = os.path.join(settings['static_path'], "upload")

# 数据库配置
settings['mysql_host'] = "db1.dqprism.com"
settings['mysql_port'] = 3307
settings['mysql_database'] = "dqv4"
settings['mysql_user'] = "daqi"
settings['mysql_password'] = "5F51692091B4031640E18E7C27430E071BC878C8"

# session配置
settings['session_secret'] = "FILUCyiulhrweuflhwesoihqwurihfbaskjdhquwvrlqkwjfv"
settings['session_timeout'] = 2592000
settings['store_options'] = {
    'redis_host': '127.0.0.1',
    'redis_port': 6379,
    'redis_pass': '',
    'max_connections': 500
}

# elk配置
settings['elk_cluster'] = {
    'redis_host': '127.0.0.1',
    'redis_port': 6379,
}

# tornado log配置
settings['blocking_log_threshold'] = 0.5

# 基础服务
settings['infra'] = "http://api1.dqprism.com"
settings['das'] = "http://das1.dqprism.com"

# wechat host
settings['qx_host'] = 'qx1.dqprism.com'
settings['platform_host'] = 'platform1.dqprism.com'
settings['helper_host'] = 'platform1.dqprism.com'

# 公众号 signatures
settings['qx_wechat_id'] = 1

settings['qx_signature'] = "ZWFkYmZmNjNmYjc3Yjk1YWFlYzg5MWMyNTllOWExNTFkZTE2MzYyMA=="
settings['platform_qianxun_signature'] = "YWNkNmIyYWExOGViOTRkODMyMzk5N2MxM2NkZDZlOTUxNmRjYzJiYQ=="
settings['helper_signature'] = "NGZiMThkZWMwMmVkMjU4OGRlMWY3Nzk1N2FiZWExMWUxODI4ODJiZQ=="

# 微信第三方平台信息
settings['component_app_id'] = 'wx5024b0daabd7bb23'
settings['component_app_secret'] = 'dad5d29cdaeb4d1d6309ab82effb27b6'
