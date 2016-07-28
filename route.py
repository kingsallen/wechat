# coding=utf-8

'''
说明:
route不需要添加v2，web网页没有维护旧版本的概念
api接口的route都加上api，非api的route会被统计为PV、UV
html route规范：项目名/业务模块，mobile/position
html route规范：项目名/api/业务模块，mobile/api/sms
'''


routes = [

    # wechat
    (r"/wechat",                "handler.common.wechat.WechatHandler"),

    # platform
    (r"/mobile/start",          "handler.platform.landing.LandingHandler"),

    # qx

    # common

]
