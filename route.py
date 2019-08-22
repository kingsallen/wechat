# coding=utf-8

""" 说明:
route不需要添加v2，web网页没有维护旧版本的概念
api接口的route都加上api，非api的route会被统计为PV、UV

common_routes: 公共的 routes,共产品线共享
platform_routes: 继承自common_routes, 供platform单独使用，一般 handler 在 platform 中，则 route 可在此编辑
qx_routes: 继承自common_routes, 供qx单独使用，一般 handler 在 qx 中，则 route 可在此编辑
help_routes: 继承自common_routes, 供help单独使用，一般 handler 在 help 中，则 route 可在此编辑

一个 handler 对应一个 route，handler 中遵守 restful 风格
例如 (
    r"/wechat",     路由
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
import handler.common.jslog
import handler.common.passport
import handler.common.position
import handler.common.profile
import handler.common.resume
import handler.common.suggest
import handler.common.usercenter
import handler.common.dictionary
import handler.common.logcollector
import handler.common.captcha
import handler.common.image
import handler.common.campaign
import handler.common.redirect
import handler.common.short_url
import handler.common.statistics
import handler.common.redpacket
import handler.common.miniapp
import handler.common.health_check

import handler.help.passport
import handler.help.releasedposition

import handler.platform.companyrelation
import handler.platform.groupcompany
import handler.platform.customize
import handler.platform.employee
import handler.platform.landing
import handler.platform.position
import handler.platform.team
import handler.platform.recom
import handler.platform.compatible
import handler.platform.user
import handler.platform.cover
import handler.help.captcha
import handler.platform.referral
import handler.platform.referral_pc
import handler.platform.award
import handler.platform.mall
import handler.platform.privacy
import handler.platform.switch
import handler.platform.radar_demo
import handler.platform.annual_summarize
import handler.platform.thirdparty

import handler.qx.app
import handler.qx.aggregation
import handler.qx.search
import handler.qx.position
import handler.qx.team
import handler.qx.company
import handler.common.permanent_qr
import handler.common.laiye_im

import handler.wechat.event

# 微信端公共的 routes
common_routes = [
    # 开发者方式
    (r"/wechat",                                     handler.wechat.event.WechatOauthHandler,                   {"event": "wechat_oauth"}),
    # 第三方授权方式
    (r"/wechat[\/]*([0-9a-z]+)*",                    handler.wechat.event.WechatThirdOauthHandler,              {"event": "wechat_thirdoauth"}),
    (r"/qr/permanent/([0-9]+)",                      handler.common.permanent_qr.PermanentQRHandler,            {"event": "permanent_qr"}),

    # app forward 给前端，展示纯前端渲染的 SPA
    (r"/app/.*",                                     handler.common.app.IndexHandler,                           {"event": "app_"}),
    (r"/login",                                      handler.common.passport.LoginHandler,                      {"event": "passport_login"}),
    (r"/logout",                                     handler.common.passport.LogoutHandler,                     {"event": "passport_logout"}),
    (r"/register[\/]*([a-z]+)*",                     handler.common.passport.RegisterHandler,                   {"event": "register_"}),
    (r"/application",                                handler.common.application.ApplicationHandler,             {"event": "application_profile"}),
    (r"/application/email",                          handler.common.application.ApplicationEmailHandler,        {"event": "application_email"}),
    (r"/positionfav/([0-9]+)",                       handler.common.position.PositionFavHandler,                {"event": "position_fav"}),
    (r"/resume/import",                              handler.common.resume.ResumeImportHandler,                 {"event": "resume_auth"}),
    (r"/resume/thirdparty",                          handler.common.resume.ThirdpartyImportHandler,             {"event": "resume_thirdparty"}),
    (r"/resume/thirdparty/liepin",                   handler.common.resume.LiepinImportCallBackHandler,         {"event": "resume_thirdparty_liepin"}),
    (r"/resume/maimai",                              handler.common.resume.MaimaiImportHandler,                 {"event": "resume_maimai"}),
    (r"/resume/liepin",                              handler.common.resume.LiepinImportHandler,                 {"event": "resume_liepin"}),
    (r"/resume/upload",                              handler.common.resume.ResumeUploadHandler,                 {"event": "resume_upload"}),
    (r"/chat/resume/upload",                         handler.common.resume.ChatbotResumeUploadHandler,          {"event": "resume_upload_from_chatbot"}),
    (r"/profile/?",                                  handler.common.profile.ProfileHandler,                     {"event": "profile_profile"}),
    (r"/profile/view/([A-Z0-9a-z_\-]+)*",            handler.common.profile.ProfileViewHandler,                 {"event": "profile_view"}),
    (r"/profile/preview/?",                          handler.common.profile.ProfilePreviewHandler,              {"event": "profile_preview"}),
    (r"/profile/custom/?",                           handler.common.profile.ProfileCustomHandler,               {"event": "profile_customcv"}),
    (r"/profile/import/?",                           handler.common.profile.ProfileImportHandler,               {"event": "profile_import"}),
    (r"/image/?",                                    handler.common.image.ImageFetchHandler,                    {"event": "image_fetch"}),
    (r"/chat/room[\/]*([0-9]+)*",                    handler.common.im.ChatRoomHandler,                         {"event": "im_room"}),
    (r"/mobot",                                      handler.common.im.MobotHandler,                            {"event": "im_mobot"}),
    (r"/im/laiye",                                   handler.common.laiye_im.LaiyeImHandler,                    {"event": "im laiye"}),
    (r"/resume/import/limit",                        handler.common.resume.ResumeImportLimit,                   {"event": "resume_import_limit"}),
    (r"/redirect",                                   handler.common.redirect.RedirectHandler,                   {"event": "redirect"}),
    (r"/redpacket/claim",                            handler.common.redpacket.RedpacketHandler,                 {"event": "redpacket_claim"}),
    (r"/api/redpacket/claim",                        handler.common.redpacket.RedpacketHandler,                 {"event": "api_redpacket_claim"}),
    (r"/s/(?P<uuid>\w+)",                            handler.common.short_url.ShortURLRedirector,               {"event": "short_url_redirect"}),
    (r"/mobile/h5/(\d+)",                            handler.common.redirect.H5DefaultHandler,                  {"event": "h5_default_page"}),
    (r"/health_check",                               handler.common.health_check.HealthcheckHandler,            {"event": "health_check"}),

    # websocket
    (r"/websocket/([A-Za-z0-9_]{1,32})",             handler.common.im.ChatWebSocketHandler),

    (r"/api/send/vcode/?",                           handler.common.passport.SendValidCodeHandler,              {"event": "send_vcode"}),
    (r"/api/upload/recomprofile/?",                  handler.platform.referral.EmployeeRecomProfileHandler,     {"event": "upload_referral_profile"}),
    (r"/api/config[\/]?",                            handler.common.app.ConfigHandler,                          {"event": "wechat_config"}),
    (r"/api/dict/city/?",                            handler.common.dictionary.DictCityHandler,                 {"event": "dict_city"}),
    (r"/api/dict/industry/?",                        handler.common.dictionary.DictIndustryHandler,             {"event": "dict_industry"}),
    (r"/api/dict/industry/([a-z]+)*?",               handler.common.dictionary.DictCustomIndustryHandler,       {"event": "dict_custom_industry"}),
    (r"/api/dict/function/?",                        handler.common.dictionary.DictFunctionHandler,             {"event": "dict_function"}),
    (r"/api/dict/country/?",                         handler.common.dictionary.DictCountryHandler,              {"event": "dict_country"}),
    (r"/api/dict/rocketmajor/?",                     handler.common.dictionary.DictRocketMajorHandler,          {"event": "dict_rocketmajor"}),
    (r"/api/dict/smscountrycode/?",                  handler.common.dictionary.DictSmsCountryCodeHandler,       {"event": "dict_smscountrycode"}),
    (r"/api/dict/mainland/college/?",                handler.common.dictionary.DictMainlandCollegeHandler,      {"event": "dict_mainland_college"}),
    (r"/api/dict/overseas/college/?",                handler.common.dictionary.DictOverseasCollegeHandler,      {"event": "dict_overseas_college"}),
    (r"/api/profile/edit/?",                         handler.common.profile.ProfileSectionHandler,              {"event": "profile_section"}),
    (r"/api/profile/new/?",                          handler.common.profile.ProfileNewHandler,                  {"event": "profile_new"}),
    (r"/api/profile/all/?",                          handler.common.profile.APIProfileHandler,                  {"event": "profile_all"}),
    (r"/api/customcv/?",                             handler.common.profile.ProfileAPICustomCVHandler,          {"event": "profile_customcv"}),
    (r"/api/position/star/?",                        handler.common.position.PositionStarHandler,               {"event": "position_star"}),
    (r"/api/resume/upload",                          handler.common.resume.APIResumeUploadHandler,              {"event": "api_resume_upload"}),
    (r"/api/resume/submit",                          handler.common.resume.ResumeSubmitHandler,                 {"event": "api_resume_submit"}),
    (r"/api/chat/resume/upload",                     handler.common.resume.ChatbotResumeSubmitHandler,          {"event": "api_resume_submit_from_chatbot"}),
    (r"/api/position/list/?",                        handler.platform.position.PositionListDetailHandler,       {"event": "api_position_list"}),
    (r"/api/position/list/sug",                      handler.platform.position.PositionListSugHandler,          {"event": "position_list_sug"}),
    (r"/api/position/search/history",                handler.platform.position.PositionSearchHistoryHandler,    {"event": "position_search_history"}),
    (r"/api/chat/unread[\/]*([0-9]+)*",              handler.common.im.UnreadCountHandler,                      {"event": "chat_"}),
    (r"/api/mobilebinded",                           handler.common.usercenter.UserMobileBindedHandler,         {"event": "user_usermobilebinded"}),
    (r"/api/cellphone[\/]*([a-z_]+)*",               handler.common.cellphone.CellphoneBindHandler,             {"event": "cellphone_"}),
    (r"/api/user/currentinfo/update",                handler.common.interest.UserCurrentUpdateHandler,          {"event": "user_currentupdate"}),
    (r"/api/user/currentinfo",                       handler.common.interest.UserCurrentInfoHandler,            {"event": "user_currentinfo"}),
    (r"/api/upload/([a-z_]*)",                       handler.common.usercenter.UploadHandler,                   {"event": "image_"}),
    (r"/api/usercenter/favpositions",                handler.common.usercenter.FavPositionHandler,              {"event": "usercenter_favpositions"}),
    (r"/api/usercenter/applyrecords[\/]*([0-9]+)*",  handler.common.usercenter.ApplyRecordsHandler,             {"event": "usercenter_applyrecords"}),
    (r"/api/usercenter",                             handler.common.usercenter.UsercenterHandler,               {"event": "usercenter_"}),
    (r"/api/resume/import",                          handler.common.resume.ResumeImportHandler,                 {"event": "resume_import"}),
    (r"/api/sug/company",                            handler.common.suggest.SuggestCompanyHandler,              {"event": "sug_company"}),
    (r"/api/sug/college",                            handler.common.suggest.SuggestCollegeHandler,              {"event": "sug_college"}),
    (r"/api/chat[\/]*([a-z]+)*",                     handler.common.im.ChatHandler,                             {"event": "chat_"}),
    (r"/api/application",                            handler.common.application.ApplicationHandler,             {"event": "application_profile"}),
    (r"/api/JSSDKError",                             handler.common.jssdkerror.JSSDKErrorHandler,               {"event": "frontend_jssdkerror"}),
    (r"/api/jslog",                                  handler.common.jslog.JSLogHandler,                         {"event": "frontend_jslog"}),
    (r"/api/collectlog",                             handler.common.logcollector.LogCollectorHandler,           {"event": "collect_log"}),
    (r"/api/captcha",                                handler.common.captcha.CaptchaHandler,                     {"event": "captcha"}),
    (r"/api/interview/statistics",                   handler.common.statistics.InterviewStatisticsHandler,      {"event": "interview_statistics"}),

    # 上传助手小程序
    (r"/api/miniapp/code",                           handler.common.miniapp.MiniappCodeHandler,                 {"event": "miniapp_code"}),
    (r"/api/resume/upload/complete",                 handler.common.resume.ResumeUploadResultHandler,           {"event": "resume_upload_complate"}),
    (r"/api/referral/upload/resume/info",            handler.common.resume.MiniappResumeUploadInfoHandler,      {"event": "resume_upload_info"}),

    # 隐私协议
    (r'/api/privacy/agree/?',                        handler.platform.privacy.PrivacyHandler,                   {"event": "api_privacy_agreement"}),
    (r'/api/privacy/is_agree/?',                     handler.platform.privacy.IsAgreePrivacyHandler,            {"event": "api_is_agree_privacy"}),
]

# 企业号的单独 routes，域名 platform.moseeker.com/m
platform_routes = [
    (r"/position/(?P<position_id>\d+)",              handler.platform.position.PositionHandler,                 {"event": "position_info"}),
    (r"/position/?",                                 handler.platform.position.PositionListHandler,             {"event": "position_list"},      'position_list'),
    (r"/start/?",                                    handler.platform.landing.LandingHandler,                   {"event": "start_landing"}),
    (r"/company/(\d+)",                              handler.platform.companyrelation.CompanyInfoRedirectHandler, {"event": "company_old_info"}, "old_company_info_page"),
    (r"/company",                                    handler.platform.companyrelation.CompanyHandler,           {"event": "company_info"},       "new_company_info_page"),
    (r"/company/team/(\d+)",                         handler.platform.team.TeamDetailHandler,                   {"event": "team_detail"}),
    (r"/company/team",                               handler.platform.team.TeamIndexHandler,                    {"event": "team_info"}),
    (r"/employee/bindemail/?",                       handler.platform.employee.EmployeeBindEmailHandler,        {"event": "employee_bindemail"}),
    (r"/employee/custominfo/?",                      handler.platform.employee.CustomInfoHandler,               {"event": "employee_custominfo"}),
    (r"/employee/binded-custominfo/?",               handler.platform.employee.BindCustomInfoHandler,           {"event": "employee_custominfo_binded"}),
    (r"/employee/binded/?",                          handler.platform.employee.BindedHandler,                   {"event": "employee_binded"}),
    (r"/employee/recom/ignore/?",                    handler.platform.recom.RecomIgnoreHandler,                 {"event": "recom_ignore"}),
    (r"/employee/recom/?",                           handler.platform.recom.RecomCandidateHandler,              {"event": "recom_normal"}),
    (r"/employee/ladder/?",                          handler.platform.employee.AwardsLadderPageHandler,         {"event": "awards_ladder_page"}),
    (r"/employee/custom_bind/gates",                 handler.platform.employee.CatesEmployeeBindHandler,        {"event": "gates employee_bind"}),
    (r"/employee/reward",                            handler.platform.award.ReferralRewardHandler,               {"event": "referral_reward"}),
    (r"/employee/mall/index",                        handler.platform.mall.MallIndexHandler,                    {"event": "mall_index"}),
    (r"/employee/mall/good/(\d+)",                   handler.platform.mall.MallGoodHandler,                     {"event": "mall_good_detail"}),
    (r"/employee/mall/order_page",                   handler.platform.mall.MallExchangePageHandler,             {"event": "mall_exchange_page"}),
    (r"/employee/referral/connections/(\d+)",        handler.platform.employee.EmployeeReferralConnectionHandler, {"event": "referral_connections"}),
    (r"/employee/referral/candidate_info/?",         handler.platform.referral.ReferralEvaluationHandler,       {"event": "referral_evaluation_info"}),

    (r'/user/survey/?',                              handler.platform.user.UserSurveyHandler,                   {'event': 'user_survey'}),
    (r'/user/ai-recom/?',                            handler.platform.user.AIRecomHandler,                      {'event': 'user_ai-recom'}),
    (r'/employee/connect_referral',                  handler.platform.user.ContactReferralInfoHandler,          {"event": "referral_contact_info"}),
    (r'/employee/survey/?',                          handler.platform.employee.EmployeeSurveyHandler,           {'event': 'employee_survey'}),
    (r'/employee/ai-recom/(\d+)',                    handler.platform.employee.EmployeeAiRecomHandler,          {'event': 'employee_ai-recom'}),
    (r'/employee/referral/policy',                   handler.platform.employee.EmployeeReferralPolicyHandler,   {"event": "referral—policy"}),
    (r'/employee/referral/invite_cards',             handler.platform.employee.ReferralInviteApplyHandler,      {"event": "referral_invite_cards"}),
    (r'/employee/referral/progress',                 handler.platform.employee.ReferralProgressHandler,         {"event": "referral_progress"}),
    (r'/employee/referral/progress_detail',          handler.platform.employee.ReferralProgressDetailHandler,   {"event": "referral_progress_detail"}),
    (r'/employee/referral/radar_cards/job_view',     handler.platform.employee.ReferralRadarCardJobViewHandler, {"event": "referral_radar_cards_job_view"}),
    (r'/employee/referral/radar_cards/seek_recom',   handler.platform.employee.ReferralRadarCardSeekRecomHandler, {"event": "referral_radar_cards_seek_recom"}),
    (r'/employee/referral/radar',                    handler.platform.employee.ReferralRadarPageHandler,        {"event": "referral_radar"}),
    (r'/employee/referral/expired',                  handler.platform.employee.ReferralExpiredPageHandler,      {"event": "referral_radar_expired"}),
    (r'/employee/bind',                              handler.platform.employee.EmployeeBindPageHandler,         {"event": "employee_bind_page"}),
    (r'/cover/no-weixin',                            handler.platform.cover.CoverHandler,                       {"event": "cover_no_weixin"}),
    (r'/position/recom/?',                           handler.platform.position.PositionRecomListHandler,        {"event": "position_recom_list"}),
    (r'/usercenter/mine/?',                          handler.common.usercenter.UsercenterMineHandler,           {"event": "usercenter_mine"}),
    (r'/employee/recom/profile/?',                   handler.platform.referral.ReferralProfileHandler,          {"event": "referral_profile"}),
    (r'/referral/confirm/?',                         handler.platform.referral.ReferralConfirmHandler,          {"event": "referral_confirm"}),
    (r'/employee/recom/profile/pc/?',                handler.platform.referral.ReferralProfilePcHandler,        {"event": "referal_confirm_pc"}),
    (r'/referral/crucial/info/?',                    handler.platform.referral.ReferralCrucialInfoHandler,      {"event": "referral_crucial_info"}),
    (r'/referral/contact_result/?',                  handler.platform.referral.ReferralResultHandler,           {"event": "referral_contact_result"}),
    (r"/joywork",                                    handler.platform.thirdparty.JoywokOauthHandler,            {"event": "joywok_oauth"}),
    (r"/thirdparty/automatic/auth",                  handler.platform.thirdparty.JoywokAutoAuthHandler,         {"event": "joywok_auto_bind_page"}),
    (r'/workwx/fivesec-skipwx',                      handler.platform.thirdparty.FiveSecSkipWXHandler,          {"event": "workwx_fivesec_skipwx"}),
    (r'/employee/qrcode',                            handler.platform.thirdparty.EmployeeQrcodeHandler,         {"event": "employee_qrcode"}),
    (r'/workwx/qrcode',                              handler.platform.thirdparty.WorkwxQrcodeHandler,           {"event": "workwx_qrcode"}),
    (r'/employee/threesec-skip',                     handler.platform.thirdparty.EmployeeThreesecSkipHandler,   {"event": "employee_threesec_skip"}),

    # 各大公司的自定义配置
    (r"/custom/emailapply/?",                        handler.platform.customize.CustomizeEmailApplyHandler,     {"event": "customize_emailapply"}),
    # pc端推荐相关
    (r"/pc/upload/profile/login/?",                  handler.platform.referral_pc.ReferralLoginHandler,         {"event": "referral_pc_login"}),
    (r"/pc/upload/profile/?",                        handler.platform.referral_pc.ReferralUploadHandler,        {"event": "referral_pc_upload"}),
    (r"/pc/api/upload/recomprofile/?",               handler.platform.referral_pc.EmployeeRecomProfilePcHandler, {"event": "referral_pc_upload_profile"}),
    (r"/pc/api/employee/recom/profile/?",            handler.platform.referral_pc.ReferralProfileAPIPcHandler,  {"event": "referral_pc_profile"}),
    (r"/radar/demo/?",                               handler.platform.radar_demo.RadarDemoHandler,              {"event": "radar_demo"}),
    (r"/api/radar/demo/?",                           handler.platform.radar_demo.RadarDemoApiHandler,           {"event": "radar_demo_api"}),

    # 年度总结
    (r"/annual/summarize",                           handler.platform.annual_summarize.AnnualSummarizeHandler,  {"event": "annual_summarize"}),
    (r"/api/annual/summarize",                       handler.platform.annual_summarize.ApiAnnualSummarizeHandler, {"event": "api_annual_summarize"}),
    (r"/api/annual/summarize/entrance",              handler.platform.annual_summarize.AnnualSummarizeEntranceHandler, {"event": "annual_summarize_entrance"}),

    (r"/api/omniauth/jw/login_code",                 handler.platform.thirdparty.JoywokInfoHandler,             {"event": "joywok_info"}),
    (r"/api/company/visitreq/?",                     handler.platform.companyrelation.CompanyVisitReqHandler,   {"event": "company_visitreq"}),
    (r"/api/company/survey/?",                       handler.platform.companyrelation.CompanySurveyHandler,     {"event": "company_survey"}),
    (r"/api/company/follow/?",                       handler.platform.companyrelation.CompanyFollowHandler,     {"event": "company_follow"}),
    (r"/api/groupcompany/check/?",                   handler.platform.groupcompany.GroupCompanyCheckHandler,    {"event": "groupcompany_check"}),
    (r"/api/employee/bind/?",                        handler.platform.employee.EmployeeBindHandler,             {"event": "employee_bind"}),
    (r"/api/employee/unbind/?",                      handler.platform.employee.EmployeeUnbindHandler,           {"event": "employee_unbind"}),
    (r"/api/employee/bind-info/?",                   handler.platform.employee.BindInfoHandler,                 {"event": "employee_bind_info"}),
    (r"/api/employee/custominfo/?",                  handler.platform.employee.CustomInfoHandler,               {"event": "api_employee_custominfo"}),
    (r"/api/employee/supply/list/?",                 handler.platform.employee.ApiEmployeeSupplyListHandler,    {"event": "api_employee_supply_list"}),
    (r"/api/employee/recommendrecords/?",            handler.platform.employee.RecommendRecordsHandler,         {"event": "employee_recommendrecords"}),
    (r"/api/employee/rewards/?",                     handler.platform.employee.AwardsHandler,                   {"event": "employee_awards"}),
    (r"/api/employee/count-policy-want",             handler.platform.employee.EmployeeInterestReferralPolicyHandler, {"event": "count_interest_policy"}),
    (r"/api/position/empnotice/?",                   handler.platform.position.PositionEmpNoticeHandler,        {"event": "position_empnotice"}),
    (r"/api/employee/rewards/rank/?",                handler.platform.employee.AwardsLadderHandler,             {"event": "awards_ladder_api"}),
    (r"/api/employee/survey/?",                      handler.platform.employee.APIEmployeeSurveyHandler,        {"event": "employee_survey_api"}),
    (r"/api/employee/praise/?",                      handler.platform.employee.PraiseHandler,                   {"event": "employee_praise"}),
    (r"/api/employee/invite_cards/?",                handler.platform.employee.EmployeeReferralCardsHandler,    {"event": "employee_referral_cards"}),
    (r"/api/employee/invite_cards/invited/?",        handler.platform.employee.EmployeeReferralInvitedHandler,  {"event": "employee_referral_cards_invited"}),
    (r"/api/employee/invite_cards/pass/?",           handler.platform.employee.EmployeeReferralPassCardsHandler, {"event": "employee_referral_pass_cards"}),
    (r"/api/employee/recom/invite/?",                handler.platform.employee.EmployeeReferralInviteApplyHandler, {"event": "employee_referral_invite_apply"}),
    (r"/api/employee/referral-progress/?",           handler.platform.employee.ReferralProgressListHandler,     {"event": "employee_referral_progress_list"}),
    (r"/api/employee/sugs/candidate-name/?",         handler.platform.employee.ReferralProgressListSearchHandler, {"event": "employee_referral_progress_list_search"}),
    (r"/api/employee/radar/?",                       handler.platform.employee.ReferralRadarHandler,            {"event": "employee_referral_radar_data"}),
    (r"/api/employee/stat/job-view/?",               handler.platform.employee.ReferralRadarCardPositionHandler, {"event": "employee_referral_radar_position_data"}),
    (r"/api/employee/stat/seek-recom/?",             handler.platform.employee.ReferralRadarCardRecomHandler,   {"event": "employee_referral_radar_seek_recom_data"}),
    (r"/api/employee/supply/info",                   handler.platform.employee.ApiEmployeeSupplyInfoHandler,    {"event": "api_employee_supply_info"}),
    (r"/api/employee/recom/subscribe",               handler.platform.employee.ApiEmployeeRecomSubscribeHandler,{"event": "api_employee_recom_subscribe"}),
    (r"/api/resend/bind/email",                      handler.platform.employee.ResendBindEmailHandler,          {"event": "resend_bind_email"}),

    (r"/api/func/wechat/?",                          handler.platform.employee.WechatSubInfoHandler,            {"event": "wechat_sub_info"}),
    (r'/api/user/survey/?',                          handler.platform.user.APIUserSurveyHandler,                {"event": "user_survey_api"}),
    (r'/api/position/recom/list/?',                  handler.platform.user.APIPositionRecomListHandler,         {"event": "position_ai-recomlist"}),
    (r'/api/recom/position/switch',                  handler.platform.user.APIPositionRecomListCloseHandler,    {"event": "position_ai-recom-position"}),
    (r'/api/usercenter/mine/?',                      handler.common.usercenter.UsercenterMyInfoHandler,         {"event": "api_my_info"}),
    (r'/api/employee/recom/profile/?',               handler.platform.referral.ReferralProfileAPIHandler,       {"event": "api_referral_profile"}),
    (r'/api/referral/confirm/?',                     handler.platform.referral.ReferralConfirmApiHandler,       {"event": "api_referral_confirm"}),
    (r'/api/referral/crucial/info/?',                handler.platform.referral.ReferralCrucialInfoApiHandler,   {"event": "api_referral_crucial_info"}),
    (r'/api/user/hr/?',                              handler.platform.companyrelation.CompanyHrInfoHandler,     {"event": "api_main_hr_info"}),
    (r'/api/user/redpacket/list/?',                  handler.platform.award.ReferralRedpacketHandler,           {"event": "api_redpacket_list"}),
    (r'/api/user/bonus/list/?',                      handler.platform.award.ReferralBonusHandler,               {"event": "api_bonus_list"}),
    (r'/api/bonus/claim/?',                          handler.platform.award.BonusClaimHandler,                  {"event": "api_bonus_cliam"}),
    (r"/api/mall/goods",                             handler.platform.mall.MallGoodsHandler,                    {"event": "mall_goods_list"}),
    (r"/api/mall/order",                             handler.platform.mall.MallExchangeHandler,                 {"event": "mall_exchange_imd"}),
    (r'/api/position/popup/?',                       handler.platform.user.PositionDetailPopupHandler,          {"event": "referral_position_detail_popup"}),
    (r'/api/position/repost/visitor_info/?',         handler.platform.user.PositionForwardFromEmpHandler,       {"event": "referral_position_forward_from"}),
    (r'/api/referral/recom_positions/?',             handler.platform.user.ReferralRelatedPositionHandler,      {"event": "referral_related_positions"}),
    (r"/api/switch[\/]*([a-z_]+)*",                  handler.platform.switch.SwitchHandler,                     {"event": "switch_"}),
    (r"/api/func/relation_tags/?",                   handler.platform.referral.ReferralCommentTagsHandler,      {"event": "referral_comment_tags"}),

    # (r"/api/func/workwx/?",                          handler.platform.thirdparty.WorkwxSubInfoHandler,            {"event": "workwx_sub_info"}),

    # 兼容老微信 url，进行302跳转
    (r"/.*",                                         handler.platform.compatible.CompatibleHandler,             {"event": "compatible"})

]
platform_routes = common_routes + platform_routes


# 聚合号的单独 routes, 域名 platform.moseeker.com/recruit
qx_routes = [

    (r"/alipaycampaign/([A-Za-z0-9_]{1,32})/company/?", handler.common.campaign.AlipayCampaignCompanyHandler,   {"event": "alipaycampaign/company"}),
    (r"/alipaycampaign/([A-Za-z0-9_]{1,32})/company/(\d+)/position/?",   handler.common.campaign.AlipayCampaignPositionHandler,        {"event": "alipaycampaign/position"}),

    (r"/api/position/(?P<position_id>\d+)",          handler.qx.position.PositionHandler,                       {"event": "position_info"}),
    (r"/api/positions[\/]?",                         handler.qx.aggregation.AggregationHandler,                 {"event": "position_aggregation"}),
    (r"/api/positions/recommend/(\d+)*",             handler.qx.position.PositionRecommendHandler,              {"event": "position_recommend"}),
    (r"/api/search/condition/*",                     handler.qx.search.SearchConditionHandler,                  {"event": "search_condition"}),
    (r"/api/search/condition/(\d+)*",                handler.qx.search.SearchConditionHandler,                  {"event": "search_condition"}),
    (r"/api/search/([a-z_]+)",                       handler.qx.search.SearchCityHandler,                       {"event": "search_condition"}),
    (r"/api/team/(\d+)",                             handler.qx.team.TeamDetailHandler,                         {"event": "team_detail"}),
    (r"/api/company/(\d+)",                          handler.qx.company.CompanyHandler,                         {"event": "company_detail"}),
    (r"/api/.*",                                     handler.qx.app.NotFoundHandler,                            {"event": "wechat_notfound"}),
    # App 路由
    (r"/.*",                                         handler.qx.app.IndexHandler,                               {"event": "app_app"}),
]
qx_routes = common_routes + qx_routes

# 招聘助手的单独 routes, 域名 platform.moseeker.com/h
help_routes = [
    (r"/position",                                   handler.help.releasedposition.ReleasedPositionHandler,     {"event": "helper_positions"}),
    (r"/hrregister/qrcode",                          handler.help.passport.RegisterQrcodeHandler,               {"event": "helper_qrcode"}),
    # 我也要招人
    (r"/api/register",                               handler.help.passport.RegisterHandler,                     {"event": "helper_register"}),
    (r"/captcha/check/?",                            handler.help.captcha.CaptchaHandler,                       {"event": "captcha_info"}),
    (r"/api/captcha/check",                          handler.help.captcha.CaptchaCheckHandler,                  {"event": "captcha_check"}),
    (r"/captcha/checked/?",                          handler.help.captcha.CaptchaChecked,                       {'event': 'captcha_checked'}),

]
help_routes = common_routes + help_routes
