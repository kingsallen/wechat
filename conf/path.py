# coding=utf-8

# ============================ 微信端Path开始 ============================
# url path
# 企业号单独链接
POSITION_PATH = '/position/{}'
POSITION_LIST = '/position'
RED_PACKET_CARD = '/mobile/redpack'
TEAM_PATH = '/company/team/{}'
COMPANY_TEAM = '/company/team'
SEARCH_FILITER = '/start'
CUSTOMIZE_EDX = '/custom/emailapply'

EMPLOYEE_VERIFY = '/app/employee/binding'
EMPLOYEE_RECOMMENDS = '/app/employee/recommends'
EMPLOYEE_CUSTOMINFO = '/employee/custominfo'
EMPLOYEE_BINDED = '/employee/binded'

PROFILE_CUSTOM_CV = '/profile/custom'

# 聚合号单独链接
GAMMA_HOME = '/app/enter'
GAMMA_POSITION = '/app/position'
GAMMA_POSITION_JD = '/app/position/{}'
GAMMA_POSITION_HOME = '/app/position/{}/home'
GAMMA_POSITION_TEAM = '/app/team/{}'
GAMMA_POSITION_COMPANY = '/app/company/{}'
GAMMA_SEARCH = '/app/search'


# 企业号、聚合号公共链接
USER_LOGIN = '/login'
USER_LOGOUT = '/logout'
RESUME_URL = '/resume/import'
RESUME_LINKEDIN = '/resume/linkedin'
APPLICATION = '/application'
APPLICATION_EMAIL = '/application/email'
COLLECT_USERINFO = '/app/asist/collect_userinfo/positionfav'
USER_CENTER = '/app/usercenter'
USERCENTER_APPLYRECORD = '/app/usercenter/applyrecords/{}'

MOBILE_VERIFY = '/app/validate_mobile'

PROFILE_VIEW = '/profile'
PROFILE_PREVIEW = '/profile/preview'
PROFILE_NEW = '/app/profile/new'

# ============================ 微信端Path结束 ============================


# ============================ 基础服务开始 ============================
# 用户服务
# Ref: https://wiki.moseeker.com/user_account_api.md
INFRA_USER_INFO = 'user'
INFRA_USER_VALID = 'user/sendCode'
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

# 申请服务
# Ref: https://wiki.moseeker.com/application-api.md
INFRA_APPLICATION = "application"
INFRA_APPLICATION_APPLY_COUNT = 'application/count/check'

# 职位服务
# REF: https://wiki.moseeker.com/position-api.md
INFRA_POSITION_RECOMMEND = 'positions/recommended'
INFRA_POSITION_LIST = 'position/list'
INFRA_POSITION_LIST_RP_EXT = 'position/rpext'
INFRA_RP_POSITION_LIST = 'position/rplist'
INFRA_RP_POSITION_LIST_SHARE_INFO = 'position/list/hb_share_info'

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

# 公司服务
COMPANY_ALL = 'company/all'
COMPANY = 'company'

# 字典服务
DICT_CONSTANT = "dict/constant"
DICT_CITIES = "dict/cities"
DICT_COLLEGE = "dict/college"
DICT_INDUSTRY = "dict/industry"
DICT_POSITION = "dict/position"

# 消息通知服务
MESSAGE_TEMPLATE = "message/template"
# ============================ 基础服务结束 ============================

# 其他外部服务
HR_WX_IMAGE_URL = "https://www.moseeker.com/common/image?url="
LINKEDIN_ACCESSTOKEN = "https://www.linkedin.com/uas/oauth2/accessToken"
LINKEDIN_AUTH = "https://www.linkedin.com/uas/oauth2/authorization"
