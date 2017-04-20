# coding=utf-8

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
    handler.common.wechat.WechatHandl `        qertyuiop[er",    handler
    {"event": "wechat_wechat"}   event事件，必须，log 需要。可由页面_功能组成，例如 company_info
)

"""

import handler.common.app
import handler.common.application
import handler.common.cellphone
import handler.common.im
import handler.common.interest
import handler.common.jssdkerror
import handler.common.passport
import handler.common.position
import handler.common.profile
import handler.common.resume
import handler.common.suggest
import handler.common.usercenter
import handler.common.dictionary

import handler.help.passport
import handler.help.releasedposition

import handler.platform.companyrelation
import handler.platform.customize
import handler.platform.employee
import handler.platform.landing
import handler.platform.position
import handler.platform.team
import handler.platform.recom

import handler.qx.wechat_oauth

import handler.wechat.event

# 微信端公共的 routes
common_routes = [
    # 开发者方式
    (r"/wechat",                                       handler.wechat.event.WechatOauthHandler,                   {"event": "wechat_oauth"}),

    # 第三方授权方式
    (r"/wechat[\/]*([0-9a-z]+)*",                      handler.wechat.event.WechatThirdOauthHandler,              {"event": "wechat_thirdoauth"}),  # passport

    # app forward 给前端，展示纯前端渲染的 SPA
    (r"/m/app/.*",                                     handler.common.app.IndexHandler,                           {"event": "app_"}),
    (r"/m/login",                                      handler.common.passport.LoginHandler,                      {"event": "passport_login"}),
    (r"/m/logout",                                     handler.common.passport.LogoutHandler,                     {"event": "passport_logout"}),
    (r"/m/register[\/]*([a-z]+)*",                     handler.common.passport.RegisterHandler,                   {"event": "register_"}),

    (r"/m/application",                                handler.common.application.ApplicationHandler,             {"event": "application_profile"}),
    (r"/m/application/email",                          handler.common.application.ApplicationEmailHandler,        {"event": "application_email"}),
    (r"/m/positionfav/([0-9]+)",                       handler.common.position.PositionFavHandler,                {"event": "position_fav"}),
    (r"/m/resume/import",                              handler.common.resume.ResumeImportHandler,                 {"event": "resume_auth"}),
    (r"/m/resume/linkedin",                            handler.common.resume.LinkedinImportHandler,               {"event": "resume_linkedin"}),

    (r"/m/profile[\/]?",                               handler.common.profile.ProfileHandler,                   {"event": "profile_profile"}),
    (r"/m/profile/preview[\/]?",                       handler.common.profile.ProfilePreviewHandler,            {"event": "profile_preview"}),
    (r"/m/profile/custom[\/]?",                        handler.common.profile.ProfileCustomHandler,             {"event": "profile_customcv"}),
    (r"/m/api/dict/city[\/]?",                         handler.common.dictionary.DictCityHandler,               {"event": "dict_city"}),
    (r"/m/api/dict/industry[\/]?",                     handler.common.dictionary.DictIndustryHandler,           {"event": "dict_industry"}),
    (r"/m/api/dict/function[\/]?",                     handler.common.dictionary.DictFunctionHandler,           {"event": "dict_function"}),
    (r"/m/api/profile/edit[\/]?",                      handler.common.profile.ProfileSectionHandler,            {"event": "profile_section"}),
    (r"/m/api/profile/new[\/]?",                       handler.common.profile.ProfileNewHandler,                {"event": "profile_new"}),

    # websocket
    (r"/m/websocket/([A-Za-z0-9_]{1,32})",             handler.common.im.ChatWebSocketHandler),

    # common api
    (r"/m/api/position/star",                          handler.common.position.PositionStarHandler,               {"event": "position_star"}),
    (r"/m/api/chat/unread[\/]*([0-9]+)*",              handler.common.im.UnreadCountHandler,                      {"event": "chat_"}),
    (r"/m/api/mobilebinded",                           handler.common.usercenter.UserMobileBindedHandler,         {"event": "user_usermobilebinded"}),
    (r"/m/api/cellphone[\/]*([a-z]+)*",                handler.common.cellphone.CellphoneBindHandler,             {"event": "cellphone_"}),
    (r"/m/api/user/currentinfo/update",                handler.common.interest.UserCurrentUpdateHandler,          {"event": "user_currentupdate"}),
    (r"/m/api/user/currentinfo",                       handler.common.interest.UserCurrentInfoHandler,            {"event": "user_currentinfo"}),
    (r"/m/api/upload/([a-z_]*)",                       handler.common.usercenter.UploadHandler,                   {"event": "image_"}),
    (r"/m/api/usercenter/favpositions",                handler.common.usercenter.FavPositionHandler,              {"event": "usercenter_favpositions"}),
    (r"/m/api/usercenter/applyrecords[\/]*([0-9]+)*",  handler.common.usercenter.ApplyRecordsHandler,             {"event": "usercenter_applyredords"}),
    (r"/m/api/usercenter",                             handler.common.usercenter.UsercenterHandler,               {"event": "usercenter_"}),
    (r"/m/api/resume/import",                          handler.common.resume.ResumeImportHandler,                 {"event": "resume_import"}),
    (r"/m/api/sug/company",                            handler.common.suggest.SuggestCompanyHandler,              {"event": "sug_company"}),
    (r"/m/api/sug/college",                            handler.common.suggest.SuggestCollegeHandler,              {"event": "sug_college"}),
    (r"/m/api/chat[\/]*([a-z]+)*",                     handler.common.im.ChatHandler,                             {"event": "chat_"}),
    (r"/m/api/application",                            handler.common.application.ApplicationHandler,             {"event": "application_profile"}),
    (r"/m/api/JSSDKError",                             handler.common.jssdkerror.JSSDKErrorHandler,               {"event": "frontend_jssdkerror"}),

    # 兼容老微信 url，进行302跳转，event 设置为 NULL
    # (r"/.*",                                         handler.common.compatible.CompatibleHandler,               {"event": "NULL"})
]

# 企业号的单独 routes
platform_routes = [
    # position
    (r"/m/position/(?P<position_id>\d+)",              handler.platform.position.PositionHandler,                 {"event": "position_info"}),
    (r"/m/position",                                   handler.platform.position.PositionListHandler,             {"event": "position_list"}),

    (r"/m/start",                                      handler.platform.landing.LandingHandler,                   {"event": "start_landing"}),
    (r"/m/company/(\d+)",                              handler.platform.companyrelation.CompanyInfoHandler,       {"event": "company_old_info"}),
    (r"/m/company",                                    handler.platform.companyrelation.CompanyHandler,           {"event": "company_info"}),
    (r"/m/company/team/(\d+)",                         handler.platform.team.TeamDetailHandler,                   {"event": "team_detail"}),
    (r"/m/company/team",                               handler.platform.team.TeamIndexHandler,                    {"event": "team_info"}),

    (r"/m/employee/bindemail[\/]?",                    handler.platform.employee.EmployeeBindEmailHandler,        {"event": "employee_bindemail"}),
    (r"/m/employee/custominfo[\/]?",                   handler.platform.employee.CustomInfoHandler,               {"event": "employee_custominfo"}),
    (r"/m/employee/binded[\/]?",                       handler.platform.employee.BindedHandler,                   {"event": "employee_binded"}),
    (r"/m/employee/recom/ignore[\/]?",                 handler.platform.recom.RecomIgnoreHandler,                 {"event": "recom_ignore"}),
    (r"/m/employee/recom[\/]?",                        handler.platform.recom.RecomCandidateHandler,              {"event": "recom_normal"}),

    # 各大公司的自定义配置
    (r"/m/custom/emailapply[\/]?",                     handler.platform.customize.CustomizeEmailApplyHandler,     {"event": "customize_emailapply"}),
    (r"/m/api/company/visitreq[\/]?",                  handler.platform.companyrelation.CompanyVisitReqHandler,   {"event": "company_visitreq"}),
    (r"/m/api/company/survey[\/]?",                    handler.platform.companyrelation.CompanySurveyHandler,     {"event": "company_survey"}),
    (r"/m/api/company/follow[\/]?",                    handler.platform.companyrelation.CompanyFollowHandler,     {"event": "company_follow"}),
    (r"/m/api/employee/bind[\/]?",                     handler.platform.employee.EmployeeBindHandler,             {"event": "employee_bind"}),
    (r"/m/api/employee/unbind[\/]?",                   handler.platform.employee.EmployeeUnbindHandler,           {"event": "employee_unbind"}),
    (r"/m/api/employee/recommendrecords[\/]?",         handler.platform.employee.RecommendRecordsHandler,         {"event": "employee_recommendrecords"}),
    (r"/m/api/employee/rewards[\/]?",                  handler.platform.employee.AwardsHandler,                   {"event": "employee_awards"}),
    (r"/m/api/position/empnotice[\/]?",                handler.platform.position.PositionEmpNoticeHandler,        {"event": "position_empnotice"}),

    # 招聘助手的 route，由于域名还没有确定，临时放这里
    (r"/h/position",                                   handler.help.releasedposition.ReleasedPositionHandler,     {"event": "helper_positions"}),
    (r"/h/register/qrcode",                            handler.help.passport.RegisterQrcodeHandler,               {"event": "helper_qrcode"}),
    # 我也要招人
    (r"/m/api/register",                               handler.help.passport.RegisterHandler,                     {"event": "helper_register"}),

]
platform_routes.extend(common_routes)


# 聚合号的单独 routes
qx_routes = [
    (r"/m/wxoauth2",                                   handler.qx.wechat_oauth.WxOauthHandler,                    {"event": "wxoauth_wxoauth"}),
]
qx_routes.extend(common_routes)


# 招聘助手的单独 routes
help_routes = [

]
help_routes.extend(common_routes)
