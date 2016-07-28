# coding=utf-8

'''
说明:
setting配置常量规范：
1.常量适用于整个系统，偏系统设置，如数据库配置、服务器路径等
2.常量不涉及具体业务逻辑（业务逻辑常量配置在constant.py中）
3.尽量考虑复用性
'''

import os
from tornado.options import define

define("port", default=8000, help="run on the given port", type=int)
define("logpath", default="logs/", help="log path")
# define("env", default="platform", help="wechat product")

settings = dict()
settings['xsrf_cookies'] = True
settings['cookie_secret'] = "EAB1D2AB05EEF04D35BA5FDF789DD6A3"
settings['debug'] = True
settings['log_level'] = "DEBUG"
settings['static_domain'] = "static2.dqprism.com"

settings['root_path'] = os.path.join(os.path.dirname(__file__), "")
settings['template_path'] = os.path.join(settings['root_path'], "template")
settings['static_path'] = os.path.join(settings['root_path'], "static")
settings['static_upload_path'] = os.path.join(settings['static_path'], "upload")

# 数据库配置 dqv4
settings['mysql_host'] = "db2.dqprism.com"
settings['mysql_port'] = 3307
settings['mysql_database'] = "dqv4"
settings['mysql_user'] = "daqi"
settings['mysql_password'] = "5F51692091B4031640E18E7C27430E071BC878C8"

# 数据库配置 analytics
settings['mysql_analytics_host'] = "db2.dqprism.com"
settings['mysql_analytics_port'] = 3307
settings['mysql_analytics_database'] = "analytics"
settings['mysql_analytics_user'] = "daqi"
settings['mysql_analytics_password'] = "5F51692091B4031640E18E7C27430E071BC878C8"

# session配置
settings['session_timeout'] = 2592000
settings['redis_host'] = "redis2.dqprism.com",
settings['redis_port'] = 6379,
settings['redis_pass'] = ""
settings['connect_timeout'] = 20