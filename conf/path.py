# coding=utf-8

# url path
WX_OAUTH_QX_PATH = '/m/wxoauth2'
POSITION_PATH = '/m/position/{}'
POSITION_LIST = '/m/position'
RED_PACKET_CARD = '/mobile/redpack'
TEAM_PATH = '/m/company/team/{}'
COMPANY_TEAM = '/m/company/team'
USER_CENTER = '/m/app/usercenter'
USER_LOGIN = '/m/login'
USER_LOGOUT = '/m/logout'
USER_CENTER_SETTING = 'm/usercenter/setting/home'
MOBILE_VERIFY = '/m/app/phone/verify'
EMPLOYEE_VERIFY = '/m/app/employee/binding'
SEARCH_FILITER = '/m/start'
CUSTOMIZE_EDX = '/m/custom/edx'

# 供侧边栏使用
OLD_POSITION = '/mobile/position'
OLD_PROFILE = '/mobile/profile'
OLD_CHAT = '/mobile/chatroom'
OLD_SYSUSER = '/mobile/sysuser'

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
INFRA_WXUSER_QRCODE_SCANRESULT = 'weixin/qrcode/scanresult'

# 申请服务
# Ref: https://wiki.moseeker.com/application-api.md
INFRA_APPLICATION = "application",
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
INFRA_PROFILE_CRAWLER = "profile/crawler"
INFRA_PROFILE_BASIC = "profile/basic"
INFRA_PROFILE_LANGUAGE = "profile/language"
INFRA_PROFILE_SKILL = "profile/skill"
INFRA_PROFILE_CREDENTIALS = "profile/credentials"
INFRA_PROFILE_EDUCATION = "profile/education"
INFRA_PROFILE_PROFILE = "profile/profile"
INFRA_PROFILE_WORKEXP = "profile/workexp"
INFRA_PROFILE_PROJECTEXP = "profile/projectexp"
INFRA_PROFILE_AWARDS = "profile/awards"
INFRA_PROFILE_WORKS = "profile/works"
INFRA_PROFILE_INTENTION = "profile/intention"

# 字典服务
DICT_CONSTANT = "dict/constant"
DICT_CITIES = "dict/cities"
DICT_COLLEGE = "dict/college"
DICT_INDUSTRY = "dict/industry"
DICT_POSITION = "dict/position"
# ============================ 基础服务结束 ============================
