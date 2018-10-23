# coding=utf-8

# ============================ 微信端Path开始 ============================
# url path
# 企业号单独链接
POSITION_PATH = '/position/{}'
POSITION_LIST = '/position'
POSITION_REFERRAL_LIST = '/position/recom'
RED_PACKET_CARD = '/mobile/redpack'
TEAM_PATH = '/company/team/{}'
COMPANY_TEAM = '/company/team'
SEARCH_FILITER = '/start'
CUSTOMIZE_EDX = '/custom/emailapply'

CAPTCHA_CHECKED = '/captcha/checked'

EMPLOYEE_VERIFY = '/app/employee/binding'
EMPLOYEE_RECOMMENDS = '/app/employee/recommends'
EMPLOYEE_RECOM = '/employee/recom'
EMPLOYEE_CUSTOMINFO = '/employee/custominfo'
EMPLOYEE_CUSTOMINFO_BINDED = '/employee/binded-custominfo'
EMPLOYEE_BINDED = '/employee/binded'
GATES_EMPLOYEE = '/employee/custom_bind/gates'
EMPLOYEE_REFERRAL_POLICY = "/employee/referral/policy"
EMPOLYEE_LADDER = "/employee/ladder"
EMPLOYEE_REWARDS_RECORD = '/app/employee/binding/rewards'

PROFILE_CUSTOM_CV = '/profile/custom'
REFERRAL_CONFIRM = "/referral/confirm"
REFERRAL_UPLOAD_PC = "/pc/upload/profile"
REFERRAL_PROFILE_PC = "/pc/api/employee/recom/profile"
MINE = "/usercenter/mine"
REFERRAL_PROFILE = "/employee/recom/profile"
REFERRAL_CRUCIAL_INFO = "/referral/crucial/info"
REFERRAL_SCAN = "/employee/recom/profile/pc"

# 聚合号单独链接
GAMMA_HOME = '/enter'
GAMMA_POSITION = '/position'
GAMMA_POSITION_HOME = '/position/{}/home'
GAMMA_POSITION_TEAM = '/team/{}'
GAMMA_POSITION_COMPANY = '/company/{}'
GAMMA_SEARCH = '/search'
GAMMA_404 = '/404'

# 企业号、聚合号公共链接
USER_LOGIN = '/login'
USER_LOGOUT = '/logout'
RESUME_URL = '/resume/import'
RESUME_LINKEDIN = '/resume/linkedin'
RESUME_MAIMAI = 'https://{}/resume/maimai{}'
RESUME_LIEPIN = 'https://{}/resume/liepin{}'
RESUME_THIRDPARTY = '/resume/thirdparty'
APPLICATION = '/application'
APPLICATION_EMAIL = '/application/email'
COLLECT_USERINFO = '/app/asist/collect_userinfo/positionfav'
USER_CENTER = '/app/usercenter'
USERCENTER_APPLYRECORD = '/app/usercenter/applyrecords'

MOBILE_VERIFY = '/app/validate_mobile'

PROFILE_VIEW = '/profile'
PROFILE_PREVIEW = '/profile/preview'
PROFILE_VISITOR_VIEW = '/profile/view/{}'
PROFILE_NEW = '/app/profile/new'

IMAGE_URL = '/image'

CAMPAIGN_COMPANY_PATH = "/alipaycampaign/{}/company"
CAMPAIGN_POSITION_PATH = "/alipaycampaign/{}/company/{}/position"

RESUME_IMPORT_FAIL = "/resume/import/limit"

# ============================ 微信端Path结束 ============================


# ============================ 基础服务开始 ============================
# 用户服务
# Ref: https://wiki.moseeker.com/user_account_api.md
INFRA_USER_INFO = 'user'
INFRA_MY_INFO = "/v1/users/{}/center-info"
INFRA_USER_VALID = 'user/sendCode'
INFRA_USER_VOICE_VALID = 'user/sendsignupcode/voice'
INFRA_USER_VERIFY = 'user/verifyCode'
INFRA_USER_COMBINE = 'user/wxbindmobile'
INFRA_USER_LOGIN = 'user/login'
INFRA_USER_LOGOUT = 'user/logout'
INFRA_USER_REGISTER = 'user/mobilesignup'
INFRA_USER_RESETPASSWD = 'user/resetpassword'
INFRA_USER_ISMOBILEREGISTERED = 'user/ismobileregistered'
INFRA_USER_APPLIED_APPLICATIONS = 'user/{}/applications'
INFRA_USER_FAV_POSITION = 'user/{}/fav-position'
INFRA_USER_SETTINGS = 'user/settings'
INFRA_WXUSER_QRCODE_SCANRESULT = 'weixin/qrcode/scanresult'
INFRA_HRUSER = 'hraccount'
INFRA_USER_EMPLOYEE_CHECK = 'user/employee/check'
INFRA_USER_EMPLOYEE = 'user/employee'
INFRA_USER_APPLYRECORD = "/v1/applications"
INFRA_USER_EMPLOYEE_REFERRAL = "/v1/referral/users/{}/employee-info"
INFRA_USER_REDPACKET_LIST = "/v1/referral/users/{}/redpackets"
INFRA_USER_BONUS_LIST = "/v1/referral/users/{}/bonus"
INFRA_USER_CLAIM_BONUS = "/v1/referral/wechat/employee/{}/bonus/claim"


# 申请服务
# Ref: https://wiki.moseeker.com/application-api.md
INFRA_APPLICATION = 'application'
INFRA_APPLICATION_APPLY_COUNT = 'application/count/check'
INFRA_APPLICATION_TYPE_APPLY_COUNT = 'application/type/count/check'

# 验证码服务
INFRA_CAPTCHA = 'position/syncVerifyInfo'
INFRA_VERIFY_PARAMS = 'position/getSyncVerifyParam'

# 职位服务
# REF: https://wiki.moseeker.com/position-api.md
INFRA_POSITION_RECOMMEND = 'positions/recommended'
INFRA_POSITION_LIST = 'position/list'
INFRA_POSITION_PERSONARECOM = 'position/personarecom'
INFRA_POSITION_EMPLOYEERECOM = 'position/employeerecom'
INFRA_POSITION_LIST_RP_EXT = 'position/rpext'
INFRA_RP_POSITION_LIST = 'position/rplist'
INFRA_RP_POSITION_LIST_SHARE_INFO = 'position/list/hb_share_info'
INFRA_THIRD_PARTY_SYNCED_POSITIONS = 'positions/thirdpartysyncedpositions'
INFRA_SUG_LIST = 'api/position/suggest'
INFRA_POSITION_FEATURE = '/api/position/feature/{}'
INFRA_POSITION_LATEST_REFUSAL_RECOM = '/user/lastest_recommend_refusal'
INFRA_POSITION_LIST_WX_TPL = '/user/refuse/recommend'
INFRA_POSITION_SEARCH_HISTORY = '/position/search/history'
INFRA_POSITION_SEARCH_HISTORY_DEL = '/position/search/history/delete'
INFRA_POSITION_BONUS = "/v1/referral/position/bonus"

# Profile 服务
# Ref: https://wiki.moseeker.com/profile-api.md
PROFILE = "profile"
PROFILE_BASIC = "profile/basic"
PROFILE_LANGUAGE = "profile/language"
PROFILE_SKILL = "profile/skill"
PROFILE_CREDENTIALS = "profile/credentials"
PROFILE_EDUCATION = "profile/education"
PROFILE_PROFILE = "profile/profile"
PROFILE_WORKEXP = "profile/workexp"
PROFILE_PROJECTEXP = "profile/projectexp"
PROFILE_AWARDS = "profile/awards"
PROFILE_WORKS = "profile/works"
PROFILE_INTENTION = "profile/intention"
PROFILE_OTHER = "profile/other"
PROFILE_IMPORT = "crawler"
PROFILE_OTHER_METADATA = "hraccount/custom/metadata"
PROFILE_CUSTOMCV_CHECK = 'profile/check/other'
PROFILE_UPLOAD = 'profile/file-parser'

# 公司服务
COMPANY_ALL = 'company/all'
COMPANY = 'company'
CREATE_COMPANY = 'api/hrcompany/add'
ONLY_REFERRAL_REWARD = "/v1/referral/company/config/pointsflag"

# 字典服务
DICT_CONSTANT = "dict/constant"
DICT_CITIES = "dict/cities"
DICT_COLLEGE = "dict/college/all"
DICT_COUNTRY = "dict/country"
DICT_INDUSTRY = "dict/industry"
DICT_POSITION = "dict/position"
DICT_MAINLAND_COLLEGE = "dict/college"
DICT_COLLEGE_BY_ID = "dict/college/abroad"

# 消息通知服务
MESSAGE_TEMPLATE = "message/template"

# chat服务
CHAT_LIMIT = "/api/v1/chat/voice/sendWarnEmail"
VOICE = "/api/v1/chat/voice/pullVoiceFile"

# 内推服务
REFERRAL_POLICY = "/v1.0/referral/conf"
INTEREST_REFERRAL_POLICY = "/v1.0/referral/policy"
MATE_NUM = "/v1/company/{}/employees-count"
UNREAD_PRAISE = "/v1/employee/{}/recent-upvote"
VOTE_PRAISE = "/v1/employee/{}/upvote/{}"
LAST_RANK_INFO = "/v1/employee/{}/last-list-info"
USER_RANK_INFO = "/v1/employee/{}/list-info"
LADDER_TYPE = "/v1/company/{}/leader-board"
BIND_REWARD = "/hraccount/company/rewardconfig"
UPDATE_RECOMMEND = "/v1/employee/{}/referral"
UPLOAD_RECOM_PROFILE = "v1/referral/file-parser"
REFERRAL_INFO = "/v1/referral-records/{}"
INFRA_REFERRAL_CONFIRM = "/v1/referral/claim"
REFERRAL_POSITION_INFO_EMPLOYEE = "/v1/employee/{}/referral-type"
INFRA_REFERRAL_CRUCIAL_INFO = "/v1/employee/{}/post-candidate-info"
REFERRAL_QRCODE = "/v1/referral/position/qrcode"
REFERRAL_POSITION_LIST = "/v1/referral/wechat/position/list"
# ============================ 基础服务结束 ============================

# 其他外部服务
LINKEDIN_ACCESSTOKEN = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_AUTH = "/oauth/v2/authorization"
MAIMAI_ACCESSTOKEN = "https://maimai.cn/oauth_login?appid={appid}&{cusdata}&login=1"
LIEPIN_ACCESSTOKEN = 'https://passport.liepin.com/mc/authlogin?state={}'
