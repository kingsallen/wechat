# coding=utf-8

# Copyright 2016 MoSeeker

'''
说明:
setting配置常量规范：
1.常量适用于整个系统，偏系统设置，如数据库配置、服务器路径等
2.常量不涉及具体业务逻辑（业务逻辑常量配置在constant.py中）
3.尽量考虑复用性
'''

import os
from util.common import ObjectDict
from tornado.options import define

define('port', default=8000, help='run on the given port', type=int)
define('logpath', default='/var/log/www/neoweixinrefer/', help='log path')
define('env', default='platform', help='wechat product')

settings = ObjectDict()
settings['xsrf_cookies'] = True
settings['cookie_secret'] = 'EAB1D2AB05EEF04D35BA5FDF789DD6A3'
settings['debug'] = True
settings['log_level'] = 'DEBUG'
settings['default_locale'] = 'zh_CN'
settings['static_domain'] = '//cdn-t.dqprism.com'
# 和前端工程师远程调试时可以开启此项,并配置remote_debug_ip选项
settings['remote_debug'] = False
# 远程/本地 前端build服务器地址
settings['remote_debug_ip'] = 'http://0.0.0.0:3003'

settings['root_path'] = os.path.join(os.path.dirname(__file__), '')
settings['template_path'] = os.path.join(settings['root_path'], 'template')
settings['locale_path'] = os.path.join(os.path.dirname(__file__), 'locale')
settings['static_path'] = os.path.join(settings['root_path'], 'static')
settings['fonts_path'] = os.path.join(settings['root_path'], 'fonts')
settings['static_upload_path'] = os.path.join(settings['static_path'], 'upload')

settings['resume_path'] = "/mnt/nfs/resume/generated"
settings['emailresume_path'] = "/mnt/nfs/resume/email"

# 数据库配置
settings['mysql_host'] = "db-t.dqprism.com"
settings['mysql_port'] = 3306
settings['mysql_database'] = "dqv4"
settings['mysql_user'] = "daqi"
settings['mysql_password'] = "5F51692091B4031640E18E7C27430E071BC878C8"
settings['async_http_client_max_clients'] = 1000
# session配置
settings['store_options'] = {
    'redis_host': 'redis-t.dqprism.com',
    'redis_port': 6379,
    'redis_pass': '',
    'max_connections': 500
}

# elk配置
settings['elk_cluster'] = {
    'redis_host': 'logredis-t.dqprism.com',
    'redis_port':  6388,
    'redis_socket_timeout': 3,
    'redis_pool_max_connections': 500
}
# elasticsearch host
settings['es'] = 'http://es-t.dqprism.com'
settings['es2'] = 'http://es2-t.dqprism.com'

# qiniu账号
settings['qiniu_ak'] = 'rMkcbmVYotu9Zxi0MqjmP5EFy6a9sZ5-h78Qt5GV'
settings['qiniu_sk'] = 'n8qRg0VJBsGyHlZJh1W887LDn2Z-2gbavg9xgoRP'
settings['qiniu_bucket'] = 'moseekertest'

#linkedin oauth
settings['linkedin_client_id'] = '75o96nwxso6gm8'
settings['linkedin_client_secret'] = '6maTLeb1PFtBPC8o'

# tornado log配置
settings['blocking_log_threshold'] = 0.5

# 基础服务
settings['infra'] = 'http://api-t.dqprism.com'
# thrift 接口
settings['zookeeper'] = {
    'address': '127.0.0.1:2181',
    'connection_pool': 10,
    'retry': 3
}
# chatbot API
settings['chatbot_api'] = 'http://mobot-t.dqprism.com/qa.api'

# wechat host
settings['m_host'] = 'platform-t.dqprism.com'
settings['qx_host'] = settings['m_host'] + '/recruit'
settings['platform_host'] = settings['m_host'] + '/m'
settings['helper_host'] = settings['m_host'] + '/h'
settings['pc_host'] = 'www-t.dqprism.com'

# 公众号 signatures
settings['qx_wechat_id'] = 276
settings['helper_wechat_id'] = 278

settings['qx_signature'] = 'MDk0OTBmZTVmYzliODI4M2E5Y2FhOTZlNzM0NmU5OWZlNzkwZmE4MQ=='
settings['helper_signature'] = 'NjM2YjY3OWEzZjIxY2ZiM2JkOTJmOWZiZTY3YmVlYmY5NGEwZDBlOA=='

# 微信第三方平台信息
settings['component_app_id'] = 'wx98aa120730a78275'
settings['component_app_secret'] = '0c79e1fa963cd80cc0be99b20a18faeb'
settings['component_encodingAESKey'] = 'YhwSCu0CGkfeaHaAE9XHXfxeX2P0r5skvlDEl1pVK2a'
settings['component_token'] = 'c37f1cd03cb111e5a2be00163e004a1f'

# cv mail notice
settings['cv_mail_sender_name'] = 'MoSeeker'
settings['cv_mail_sender_email'] = 'emailtest@moseeker.net'
settings['cv_mail_sender'] = settings['cv_mail_sender_name'] + " <" + settings['cv_mail_sender_email'] + ">"
settings['cv_mail_smtpserver'] = 'mail.moseeker.net'
settings['cv_mail_username'] = 'emailtest'
settings['cv_mail_password'] = 'emts%2dqv'
# rabbitmq
settings['rabbitmq_host'] = 'rabbitmq-t.dqprism.com'
settings['rabbitmq_port'] = 5672
settings['rabbitmq_username'] = "daqi"
settings['rabbitmq_password'] = "2U3sanQJ"
settings['rabbitmq_connection_attempts'] = 3
settings['rabbitmq_heartbeat_interval'] = 3600


