# coding=utf-8

# url path
PATH_AUTH = '/mobile/auth'
WX_OAUTH_QX_PATH = '/m/wxoauth2'
POSITION_PATH = '/m/position/{}'
RED_PACKET_CARD = '/mobile/redpack'
TEAM_PATH = '/m/company/team/{}'
COMPANY_TEAM = '/m/company/team'

OLD_POSITION_PATH = '/mobile/position'

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
# ============================ 基础服务结束 ============================
