# coding=utf-8

# Copyright 2016 MoSeeker

""" 说明:
route不需要添加v2，web网页没有维护旧版本的概念
api接口的route都加上api，非api的route会被统计为PV、UV

common_routes: 公共的 routes,共产品线共享
platform_routes: 继承自common_routes, 供platform单独使用
qx_routes: 继承自common_routes, 供qx单独使用
help_routes: 继承自common_routes, 供help单独使用

"""

# 微信端公共的 routes
common_routes = [
    # wechat
    (r"/wechat", "handler.common.wechat.WechatHandler"),
]

# 企业号的单独 routes
platform_routes = [
    (r"/mobile/start",
     "handler.platform.landing.LandingHandler"),

    (r"/mobile/company/([0-9]*)",
     "handler.platform.companyrelation.CompanyHandler"),

    (r"/api/mobile/company/visitreq",
     "handler.platform.companyrelation.CompanyVisitReqHandler"),

    (r"/api/mobile/company/follow",
     "handler.platform.companyrelation.CompanyFollowHandler"),

    (r"/api/mobile/cellphone",
     "handler.platform.cellphone.CellphoneBindHandler"),

    # Testing url, delete when releasing
    (r"/mobile/test",
     "tests.dao.user.TestCompanyVisitReqHandler"),
]
platform_routes.extend(common_routes)


# 聚合号的单独 routes
qx_routes = [

]
qx_routes.extend(common_routes)


# 招聘助手的单独 routes
help_routes = [

]
help_routes.extend(common_routes)
