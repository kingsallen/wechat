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
    {"event": "wechat_wechat"}   event事件，必须，log 需要。可由页面_功能组成，例如 company_info
)

"""

# 微信端公共的 routes
common_routes = [
    # 开发者方式
    (r"/wechat",                                       "handler.wechat.event.WechatOauthHandler",                   {"event": "wechat_oauth"}),
    # 第三方授权方式
    (r"/wechat[\/]*([0-9a-z]+)*",                      "handler.wechat.event.WechatThirdOauthHandler",              {"event": "wechat_thirdoauth"}),  # passport
    (r"/m/user/([a-z]*)",                              "handler.common.passport.LoginHandler",                      {"event": "user_login"}),
    # position
    (r"/m/position/([0-9]+)",                          "handler.common.position.PositionHandler",                   {"event": "position_info"}),
    (r"/m/position",                                   "handler.common.position.PositionListHandler",               {"event": "position_list"}),

    # app forward 给前端，展示纯前端渲染的 SPA
    (r"/m/app/([a-zA-Z][a-zA-Z0-9]*)?.*/g",            "handler.common.app.IndexHandler",                           {"event": "app_"}),

    # common api
    (r"/m/api/position/star",                          "handler.common.position.PositionStarHandler",               {"event": "position_star"}),
    (r"/m/api/chat/unread[\/]*([0-9]+)*",              "handler.common.im.UnreadCountHandler",                      {"event": "chat_"}),
    (r"/m/api/mobilebinded",                           "handler.common.user.UserMobileBindedHandler",               {"event": "user_usermobilebinded"}),
    (r"/m/api/cellphone",                              "handler.common.cellphone.CellphoneBindHandler",             {"event": "cellphone_bind"}),
    (r"/m/api/user/currentinfo",                       "handler.common.interest.UserCurrentInfoHandler",            {"event": "user_currentinfo"}),
    (r"/m/api/upload/([a-z]*)",                        "handler.common.usercenter.UploadHandler",                   {"event": "image_"}),
    (r"/m/api/usercenter/favpositions",                "handler.common.usercenter.FavpositionHandler",              {"event": "usercenter_favpositions"}),
    (r"/m/api/usercenter/applyrecords[\/]*([0-9]+)*",  "handler.common.usercenter.ApplyrecordsHandler",             {"event": "usercenter_applyredords"}),
    (r"/m/api/usercenter",                             "handler.common.usercenter.UsercenterHandler",               {"event": "usercenter_"}),

    # 兼容老微信 url，进行302跳转，event 设置为 NULL
    (r"/.*",                                           "handler.common.compatible.CompatibleHandler",               {"event": "NULL"})

]

# 企业号的单独 routes
platform_routes = [
    (r"/m/start",                                      "handler.platform.landing.LandingHandler",                   {"event": "start_landing"}),
    (r"/m/company/(\d+)",                              "handler.platform.companyrelation.CompanyInfoHandler",       {"event": "company_old_info"}),
    (r"/m/company",                                    "handler.platform.companyrelation.CompanyHandler",           {"event": "company_info"}),
    (r"/m/company/team/(\d+)",                         "handler.platform.team.TeamDetailHandler",                   {"event": "team_detail"}),
    (r"/m/company/team",                               "handler.platform.team.TeamIndexHandler",                    {"event": "team_info"}),

    (r"/m/api/company/visitreq",                       "handler.platform.companyrelation.CompanyVisitReqHandler",   {"event": "company_visitreq"}),
    (r"/m/api/company/survey",                         "handler.platform.companyrelation.CompanySurveyHandler",     {"event": "company_survey"}),
    (r"/m/api/company/follow",                         "handler.platform.companyrelation.CompanyFollowHandler",     {"event": "company_follow"})
]
platform_routes.extend(common_routes)


# 聚合号的单独 routes
qx_routes = [
    (r"/m/wxoauth2",                                   "handler.qx.wechat_oauth.WxOauthHandler",                    {"event": "wxoauth_wxoauth"})
]
qx_routes.extend(common_routes)


# 招聘助手的单独 routes
help_routes = [

]
help_routes.extend(common_routes)
