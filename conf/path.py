# coding=utf-8

# url path
WX_OAUTH_QX_PATH = '/m/wxoauth2'
POSITION_PATH = '/m/position/{}'
POSITION_LIST = '/m/position'
RED_PACKET_CARD = '/mobile/redpack'
TEAM_PATH = '/m/company/team/{}'
COMPANY_TEAM = '/m/company/team'
USER_LOGIN = '/m/login'
USER_LOGOUT = '/m/logout'
SEARCH_FILITER = '/m/start'
CUSTOMIZE_EDX = '/m/custom/emailapply'
APPLICATION = '/m/application'
COLLECT_USERINFO = '/m/app/asist/collect_userinfo/positionfav'
USER_CENTER = '/m/app/usercenter'
MOBILE_VERIFY = '/m/app/validate_mobile'
EMPLOYEE_VERIFY = '/m/app/employee/binding'
EMPLOYEE_RECOMMENDS = '/m/app/employee/recommends'
USERCENTER_APPLYRECORD = '/m/app/usercenter/applyrecords/{}'

PROFILE_VIEW = '/m/profile'
PROFILE_NEW = '/m/app/profile/new'

# 供侧边栏使用
OLD_POSITION = '/mobile/position'
OLD_PROFILE = '/mobile/profile'
OLD_CHAT = '/mobile/chatroom'
OLD_SYSUSER = '/mobile/sysuser'
OLD_APPLICATION = '/mobile/application'

HR_WX_IMAGE_URL = "https://www.moseeker.com/common/image?url="

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
INFRA_HRUSER = 'hraccount'

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
