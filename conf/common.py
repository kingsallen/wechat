# coding=utf-8

"""
说明:
constant配置常量规范：
1.常量涉及通用业务逻辑定义，即同时适用于聚合号和企业号
2.系统常量定义在顶部，业务常量定义在底部。
3.使用分割线区分系统、业务常量
4.常量配置添加注释

常量使用大写字母，字符串需要时标注为unicode编码
例如 SUCCESS = "成功"
"""

# ++++++++++系统常量++++++++++

QX_HOST = "qx.moseeker.com"
# URL consts
WXOAUTH_URL = "/wxoauth"

# Weixin API url
WX_OAUTH_GET_CODE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_%s&state=%s#wechat_redirect"
WX_THIRD_OAUTH_GET_CODE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_%s&state=%s&component_appid=%s#wechat_redirect"
WX_OAUTH_GET_ACCESS_TOKEN = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"
WX_THIRD_OAUTH_GET_ACCESS_TOKEN = "https://api.weixin.qq.com/sns/oauth2/component/access_token?appid=%s&code=%s&grant_type=authorization_code&component_appid=%s&component_access_token=%s"
WX_OAUTH_GET_USERINFO = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN"

# Wechat Account Type
WECHAT_TYPE_SUBSCRIPTION = 0
WECHAT_TYPE_UNCONFIRM_SUBSCRIPTION = 2
WECHAT_TYPE_SERVICE = 1
WECHAT_TYPE_UNCONFIRM_SERVICE = 3

# status_code默认错误返回
RESPONSE_SUCCESS = "success"
RESPONSE_FAILED = "failed"

# 环境
ENV = "new_wechat"
ENV_PLATFORM = "platform"
ENV_QX = "qx"
ENV_HELP = "help"

# 微信客户端类型
CLIENT_WECHAT = 1
CLIENT_NON_WECHAT = 2
CLIENT_TYPE_IOS = 100
CLIENT_TYPE_ANDROID = 101
CLIENT_TYPE_WIN = 102
CLIENT_TYPE_UNKNOWN = 103

# 入库字段类型
TYPE_INT = 1
TYPE_JSON = 2
TYPE_FLOAT = 3
TYPE_TIMESTAMP = 4
TYPE_STRING = 5  # 会过滤xss
TYPE_STRING_ORIGIN = 6  # 不过滤xss

# 日期、时间规范
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT_PURE = "%Y%m%d%H%M%S"
TIME_FORMAT_DATEONLY = "%Y-%m-%d"
TIME_FORMAT_MINUTE = "%Y-%m-%d %H:%M"
TIME_FORMAT_MSEC = "%Y-%m-%d %H:%M:%S.%f"
JD_TIME_FORMAT_DEFAULT = "-"
JD_TIME_FORMAT_FULL = "{0}-{:0>2}-{:0>2}"
JD_TIME_FORMAT_JUST_NOW = "刚刚"
JD_TIME_FORMAT_TODAY = "今天 {:0>2}:{:0>2}"
JD_TIME_FORMAT_YESTERDAY = "昨天 {:0>2}:{:0>2}"
JD_TIME_FORMAT_THIS_YEAR = "{:0>2}-{:0>2}"

# 数据库规范化常量
STATUS_INUSE = 1
STATUS_UNUSE = 0

# ++++++++++业务常量+++++++++++
# Cookie name
COOKIE_SESSIONID = "FY823UTGIPUSDFP8Q*ZKP$GTYXIVQWQFUGS"

# Cache 相关常量
VIEWER_TYPE_NEW = 1
VIEWER_TYPE_OLD = 0


# 职位相关，主要涉及到职位，职位列表，搜索页
# 招聘类型
CANDIDATE_SOURCE = {
    "0": "社招",
    "1": "校招",
}

# 工作性质
EMPLOYMENT_TYPE = {
    "0": "全职",
    "1": "兼职",
    "2": "合同工",
    "3": "实习",
}

# 学历
DEGREE = {
    "1": "大专",
    "2": "本科",
    "3": "硕士",
    "4": "MBA",
    "5": "博士",
    "6": "中专",
    "7": "高中",
    "8": "博士后",
    "9": "初中"
}

# 及以上 工作经验、学历中使用
POSITION_ABOVE = "及以上"
EXPERIENCE_UNIT = "年"
