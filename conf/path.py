# coding=utf-8

# url path
WX_OAUTH_QX_PATH = '/m/wxoauth2'
POSITION_PATH = '/m/position/{}'
RED_PACKET_CARD = '/mobile/redpack'
TEAM_PATH = '/m/company/team/{}'
COMPANY_TEAM = '/m/company/team'
USER_CENTER = '/m/usercenter'
USER_LOGIN = '/m/login'
USER_LOGOUT = '/m/logout'
USER_CENTER_SETTING = 'm/usercenter/setting/home'
MOBILE_VERIFY = '/m/app/phone/verify'

# 供侧边栏使用
OLD_POSITION = '/mobile/position'
OLD_PROFILE = '/mobile/profile'
OLD_CHAT = '/mobile/chatroom'
OLD_SYSUSER = '/mobile/sysuser'

# ============================ 基础服务开始 ============================
# 用户服务
# REFERER: https://wiki.moseeker.com/user_account_api.md
USER_INFO = 'user'
USER_VALID = 'user/sendCode'
USER_VERIFY = 'user/verifyCode'
USER_COMBINE = 'user/wxbindmobile'
USER_LOGIN_PATH = 'user/login'
USER_APPLIED_APPLICATIONS = 'user/{}/applications'
USER_FAV_POSITION = 'user/{}/fav-position'

# 申请服务
# REFERER: https://wiki.moseeker.com/application-api.md
APPLICATION_APPLY_COUNT = 'application/count/check'

# 职位服务
# REFERER: https://wiki.moseeker.com/position-api.md
POSITION_RECOMMEND = 'positions/recommended'
POSITION_LIST = 'position/list'
POSITION_LIST_RP_EXT = 'position/rpext'
RP_POSITION_LIST = 'position/rplist'
RP_POSITION_LIST_SHARE_INFO = 'position/list/hb_share_info'
# ============================ 基础服务结束 ============================
