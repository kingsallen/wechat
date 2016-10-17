# coding=utf-8

# Copyright 2016 MoSeeker

""" 说明:
route不需要添加v2，web网页没有维护旧版本的概念
api接口的route都加上api，非api的route会被统计为PV、UV

common_routes: 公共的 routes,共产品线共享
platform_routes: 继承自common_routes, 供platform单独使用，一般 handler 在 platform 中，则 route 可在此编辑
qx_routes: 继承自common_routes, 供qx单独使用，一般 handler 在 qx 中，则 route 可在此编辑
help_routes: 继承自common_routes, 供help单独使用，一般 handler 在 help 中，则 route 可在此编辑

"""

# 微信端公共的 routes
common_routes = [
    # wechat
    (r"/wechat",
     "handler.common.wechat.WechatHandler"),

    (r"/mobile/company/([0-9]*)",
     "handler.platform.companyrelation.CompanyHandler"),

    (r"/api/company/visitreq",
     "handler.platform.companyrelation.CompanyVisitReqHandler"),

    (r"/api/company/follow",
     "handler.platform.companyrelation.CompanyFollowHandler"),

    (r"/api/cellphone",
     "handler.platform.cellphone.CellphoneBindHandler"),

    # Testing url, delete when releasing
    (r"/mobile/test",
     "tests.dao.user.TestCompanyVisitReqHandler")
]

# 企业号的单独 routes
platform_routes = [
    (r"/mobile/start",
     "handler.platform.landing.LandingHandler")
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
