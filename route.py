# coding=utf-8

# Copyright 2016 MoSeeker

""" 说明:
route不需要添加v2，web网页没有维护旧版本的概念
api接口的route都加上api，非api的route会被统计为PV、UV

common_routes: 公共的 routes,共产品线共享
platform_routes: 继承自common_routes, 供platform单独使用，一般 handler 在 platform 中，则 route 可在此编辑
qx_routes: 继承自common_routes, 供qx单独使用，一般 handler 在 qx 中，则 route 可在此编辑
help_routes: 继承自common_routes, 供help单独使用，一般 handler 在 help 中，则 route 可在此编辑

!!! 注意
!!! route 都以/m/，nginx 会判断，并将所有该路由都会调用新微信，非/m/开头，会调用老微信 !!!

一个 handler 对应一个 route，handler 中遵守 restful 风格
例如 (
    r"/m/wechat",     路由
    "handler.common.wechat.WechatHandler",    handler
    {"event": "wechat_wechat"}   event事件，必须，log 需要
)

"""

# 微信端公共的 routes
common_routes = [
    # wechat
    (r"/m/wechat",                       "handler.common.wechat.WechatHandler",                       {"event": "wechat_wechat"}),
    (r"/m/login",                        "handler.common.login.LoginHandler",                         {"event": "login_login"}),

    # Testing url, delete when releasing
    (r"/m/test",                         "tests.dao.user.TestCompanyVisitReqHandler",                 {"event": "test_test"})
]

# 企业号的单独 routes
platform_routes = [
    (r"/m/start",                        "handler.platform.landing.LandingHandler",                   {"event": "start_landing"}),
    (r"/m/company/([0-9]*)",             "handler.platform.companyrelation.CompanyHandler",           {"event": "company_info"}),
    (r"/m/interest",                     "handler.platform.interest.InterestHandler",                {"event": "interest"}),

    (r"/m/api/company/visitreq",         "handler.platform.companyrelation.CompanyVisitReqHandler",   {"event": "company_visitreq"}),
    (r"/m/api/company/follow",           "handler.platform.companyrelation.CompanyFollowHandler",     {"event": "company_follow"}),
    (r"/m/api/cellphone",                "handler.platform.cellphone.CellphoneBindHandler",           {"event": "cellphone_bind"}),
]
platform_routes.extend(common_routes)


# 聚合号的单独 routes
qx_routes = [
    (r"/m/wxoauth2",                     "handler.qx.wechat_oauth.WxOauthHandler",                    {"event": "wxoauth_wxoauth"})
]
qx_routes.extend(common_routes)


# 招聘助手的单独 routes
help_routes = [

]
help_routes.extend(common_routes)
