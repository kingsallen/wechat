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
define('logpath', default='logs/', help='log path')
define('env', default='platform', help='wechat product')

settings = ObjectDict()
settings['xsrf_cookies'] = True
settings['cookie_secret'] = 'EAB1D2AB05EEF04D35BA5FDF789DD6A3'
settings['debug'] = True
settings['log_level'] = 'DEBUG'
settings['static_domain'] = '//static2.dqprism.com'
# 和前端工程师远程调试时可以开启此项,并配置remote_debug_ip选项
settings['remote_debug'] = False
# 远程/本地 前端build服务器地址
settings['remote_debug_ip'] = 'http://0.0.0.0:3003'

settings['root_path'] = os.path.join(os.path.dirname(__file__), '')
settings['template_path'] = os.path.join(settings['root_path'], 'template')
settings['static_path'] = os.path.join(settings['root_path'], 'static')
settings['static_upload_path'] = os.path.join(settings['static_path'], 'upload')

settings['resume_path'] = "/mnt/nfs/resume/generated"
settings['emailresume_path'] = "/mnt/nfs/resume/email"

# 数据库配置
settings['mysql_host'] = 'db2.dqprism.com'
settings['mysql_port'] = 3307
settings['mysql_database'] = 'dqv4'
settings['mysql_user'] = 'daqi'
settings['mysql_password'] = '5F51692091B4031640E18E7C27430E071BC878C8'

# session配置
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

# qiniu账号
settings['qiniu_ak'] = 'rMkcbmVYotu9Zxi0MqjmP5EFy6a9sZ5-h78Qt5GV'
settings['qiniu_sk'] = 'n8qRg0VJBsGyHlZJh1W887LDn2Z-2gbavg9xgoRP'
settings['qiniu_bucket'] = 'moseekertest'

#linkedin oauth
settings['linkedin_client_id'] = '7559ny1z1ti7d2'
settings['linkedin_client_secret'] = 'KtwstrKAGhI4MUVf'

# tornado log配置
settings['blocking_log_threshold'] = 0.5

# 微信支付
settings['apikey'] = 'xxxx'
settings['cert_file_path'] = 'xxx/apiclient_cert.pem'
settings['key_file_path'] = 'xxx/apiclient_key.pem'
settings['wechat_pay_appid'] = 'wx....'
settings['wechat_pay_mchid'] = 'xxxx'

# 基础服务
settings['infra'] = 'http://api2.dqprism.com'

# wechat host
settings['qx_host'] = 'qx2.dqprism.com'
settings['platform_host'] = 'platform2.dqprism.com'
settings['helper_host'] = 'platform2.dqprism.com'
settings['pc_host'] = 'www2.dqprism.com'

# 公众号 signatures
settings['qx_wechat_id'] = 1
settings['helper_wechat_id'] = 9

settings['qx_signature'] = 'ZWFkYmZmNjNmYjc3Yjk1YWFlYzg5MWMyNTllOWExNTFkZTE2MzYyMA=='
settings['helper_signature'] = 'NGZiMThkZWMwMmVkMjU4OGRlMWY3Nzk1N2FiZWExMWUxODI4ODJiZQ=='

# 微信第三方平台信息
settings['component_app_id'] = 'wxee9d0552f867959b'
settings['component_app_secret'] = '9ebcf7f4b719bf1384184ca50f2b82aa'
settings['component_encodingAESKey'] = 'YhwSCu0CGkfeaHaAE9XHXfxeX2P0r5skvlDEl1pVK2a'
settings['component_token'] = 'c37f1cd03cb111e5a2be00163e004a1f'

# cv mail notice
settings['cv_mail_sender_name'] = 'MoSeeker'
settings['cv_mail_sender_email'] = 'emailtest@moseeker.net'
settings['cv_mail_sender'] = settings['cv_mail_sender_name'] + " <" + settings['cv_mail_sender_email'] + ">"
settings['cv_mail_smtpserver'] = 'mail.moseeker.net'
settings['cv_mail_username'] = 'emailtest'
settings['cv_mail_password'] = 'emts%2dqv'
