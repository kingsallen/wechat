# coding=utf-8


"""
说明:
constant配置常量规范：
1.常量涉及通用业务逻辑定义，即同时适用于聚合号和企业号
2.系统常量定义在顶部，业务常量定义在底部。
3.使用分割线区分系统、业务常量
4.常量配置添加注释

常量使用大写字母
例如 SUCCESS = "成功"
"""
from util.common import ObjectDict

# ++++++++++系统常量++++++++++

# Wechat Account Type
WECHAT_TYPE_SUBSCRIPTION = 0
WECHAT_TYPE_UNCONFIRM_SUBSCRIPTION = 2
WECHAT_TYPE_SERVICE = 1
WECHAT_TYPE_UNCONFIRM_SERVICE = 3

# USER_USER注册来源
WECHAT_REGISTER_SOURCE_QX = 1
WECHAT_REGISTER_SOURCE_PLATFORM = 2

# USER_WX_USER创建、更新来源
WX_USER_SOURCE_SUBSCRIBE = 1
WX_USER_SOURCE_UNSUBSCRIBE = 2
WX_USER_SOURCE_SUBSCRIPTION = 3
WX_USER_SOURCE_OAUTH = 4
WX_USER_SOURCE_UPDATE_ALL = 5
WX_USER_SOURCE_UPDATE_SHORT = 6
WX_USER_SOURCE_OAUTH_UPDATE = 7
WX_USER_SOURCE_SCAN = 8
WX_USER_SOURCE_UPDATE_UNIONID = 9
WX_USER_SOURCE_UPDATE_SYSUSER = 10
WX_USER_SOURCE_UPDATE = 11
WX_USER_SOURCE_IWANTYOU = 12 # 微信端我也要招人注册

WX_USER_SUBSCRIBED = 1
WX_USER_UNSUBSCRIBED = 0

# 环境
ENV = "new_wechat"
ENV_PLATFORM = "platform"
ENV_QX = "qx"
ENV_HELP = "help"

"""appid for infra"""
APPID = {
    ENV_QX:       "5",
    ENV_PLATFORM: "6",
    ENV_HELP:     "7"
}

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
JD_TIME_FORMAT_FULL = "{}-{:0>2}-{:0>2}"
JD_TIME_FORMAT_JUST_NOW = "刚刚"
JD_TIME_FORMAT_TODAY = "今天 {:0>2}:{:0>2}"
JD_TIME_FORMAT_YESTERDAY = "昨天 {:0>2}:{:0>2}"

# 数据库规范化常量
STATUS_INUSE = 1
STATUS_UNUSE = 0

# 页面 meta 属性
PAGE_META_TITLE = "仟寻招聘"
PAGE_POSITION_INFO = "职位详情"
PAGE_COMPANY_INFO = "公司详情"
PAGE_REGISTER = "注册"
PAGE_FORGET_PASSWORD = "忘记密码"


# ++++++++++REDIS KEYS++++++++
SESSION_USER = "SESSION_USER_{0}_{1}"
SESSION_ID = "{0}:{1}"
# hr帐号的 session key
SESSION_USER_HR_ACCOUNT = 'user_hr_account_{}'
# hr平台绑定微信后的 pub/sub key
SESSION_WX_BINDING = 'wx_binding_{}'
# Email投递创建Redis格式(邮件解析, 提醒脚本都会用到)
FORMAT_EMAIL_CREATE = "EMAIL_CREATE:{}"  #


# ++++++++++业务常量+++++++++++
# Cookie name
COOKIE_SESSIONID = "5MA8A989"
COOKIE_MVIEWERID = "mviewer_id"
COOKIE_CODE = "JKKSDF89"
COOKIE_DEBUG_AUTH = "cda"
COOKIE_MOBILE_CODE = "ER2T45YU"
COOKIE_MOBILE_REGISTER = "E45645YU"
MVIEWER_ID = "{0}:{1}"

# Cache 相关常量
VIEWER_TYPE_NEW = 1
VIEWER_TYPE_OLD = 0

# API_STATUS
API_SUCCESS = 0
API_FAILURE = 1
API_WARNING = 2

# 通用状态的布尔值
YES = 1
NO = 0

# 老数据库的通用状态
# TODO (yiliang) 要改！
OLD_YES = 0
OLD_NO = 1

# 我感兴趣状态常量
FAV_YES = 0
FAV_NO = 1
FAV_INTEREST = 2

# employee-binding
EMPLOYEE_BINDING_SUCCESS = 0
EMPLOYEE_BINDING_NEED_VALIDATE = 1
EMPLOYEE_UNBINDING = 1
EMPLOYEE_BINDING_FAILURE = 2


# 职位相关，主要涉及到职位，职位列表，搜索页
# 招聘类型
CANDIDATE_SOURCE = {
    "0": "社招",
    "1": "校招",
    "2": "定向招聘"
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
    "0": "",
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

# 公司相关
SCALE = {
    "0": "",
    "1": "少于15人",
    "2": "15-50人",
    "3": "50-150人",
    "4": "150-500人",
    "5": "500-1000人",
    "6": "1000-5000人",
    "7": "5000-10000人",
    "8": "10000人以上",
}

# 默认图标
SYSUSER_HEADIMG = "weixin/images/hr-avatar-default.png"
HR_HEADIMG = "weixin/images/default-HR.png"
COMPANY_HEADIMG = "common/images/default-company-logo.jpg"

# 招聘进度全状态(对应hr_points_conf中template_id)
RECRUIT_STATUS_RECOMCLICK_ID = 7  # 转发被点击
RECRUIT_STATUS_FULL_RECOM_INFO_ID = 13  # 完善被推荐人
RECRUIT_STATUS_APPLY_ID = 1  # 提交简历成功
RECRUIT_STATUS_CVCHECKED_ID = 6  # 简历被查看
RECRUIT_STATUS_CVFORWARDED_ID = 8  # 转发简历MGR评审
RECRUIT_STATUS_CVPENDING_ID = 9  # MGR评审后表示先等待
RECRUIT_STATUS_CVPASSED_ID = 10  # 评审通过要求面试
RECRUIT_STATUS_INTERVIEW_ID = 2  # HR安排面试
RECRUIT_STATUS_INTERVIEWPENDING_ID = 5  # MGR面试后表示先等待
RECRUIT_STATUS_OFFERED_ID = 12  # 发出录取通知
RECRUIT_STATUS_OFFERACCEPTED_ID = 11  # 接受录取通知
RECRUIT_STATUS_HIRED_ID = 3  # 入职
RECRUIT_STATUS_REJECT_ID = 4  # 拒绝

# 职位状态
RP_POSITION_STATUS_NONE = 0
RP_POSITION_STATUS_CLICK = 1
RP_POSITION_STATUS_APPLY = 2
RP_POSITION_STATUS_BOTH = 3

# 国际编码列表
NATIONAL_CODE = [
    {'id': 1, 'code': '+86', 'country': '中国'}
]

MOBILE_CODE_OPT_TYPE = ObjectDict({
    'code_register': 1,
    'forget_password': 2,
    'valid_old_mobile': 3,
    'change_mobile': 4
})

# 简历导入
RESUME_WAY_MOSEEKER_PC = "0"
RESUME_WAY_MOSEEKER = "1"
RESUME_WAY_51JOB = "2"
RESUME_WAY_LIEPIN = "3"
RESUME_WAY_ZHILIAN = "4"
RESUME_WAY_LINKEDIN = "5"

RESUME_WAY_SPIDER = {
    RESUME_WAY_51JOB: "51job.html",
    RESUME_WAY_ZHILIAN: "zhaopin.html",
    RESUME_WAY_LIEPIN: "liepin.html"
}

RESUME_WAY_TO_INFRA = {
    RESUME_WAY_51JOB: 1,
    RESUME_WAY_LIEPIN: 2,
    RESUME_WAY_ZHILIAN: 3,
    RESUME_WAY_LINKEDIN: 4
}


# ============= 红包相关常量 =============
# 红包锁字符串模版
RP_LOCK_FMT = "rplock:%s:%s:%s"
RP_LOCKED = 1

# RP_ITEM 状态常量
# 默认初始状态
RP_ITEM_STATUS_DEFAULT = 0
# 发送了消息模成功
RP_ITEM_STATUS_SENT_WX_MSG_SUCCESS = 1
# 发送消息模板失败, 尝试直接发送有金额的红包
RP_ITEM_STATUS_SENT_WX_MSG_FAILURE = 2
# 打开刮刮卡，点击红包数字前
RP_ITEM_STATUS_CARD_LINK_OPENED = 3
# 点击刮刮卡上红包数字后
RP_ITEM_STATUS_CARD_OPENED = 4
# 发送红包前，校验 current_user.qxuser 不通过，红包停发
RP_ITEM_STATUS_CURRENT_USER_CHECK_FAILURE = 5
# 发送红包前，校验刮刮卡中的 hb_item 不通过，红包停发
RP_ITEM_STATUS_CARD_CHECK_FAILURE = 6
# 跳过模版消息直接发送红包失败
RP_ITEM_STATUS_NO_WX_MSG_MONEY_SEND_FAILURE = 7
# 发送消息模板后成功发送了红包
RP_ITEM_STATUS_WX_MSG_MONEY_SENT_SUCCESS = 100
# 跳过发送消息模板后成功发送了红包
RP_ITEM_STATUS_NO_WX_MSG_MONEY_SENT_SUCCESS = 101
# 发送了 0 元红包的消息模板
RP_ITEM_STATUS_ZERO_AMOUNT_WX_MSG_SENT = -1

# 红包发送对象
RED_PACKET_CONFIG_TARGET_EMPLOYEE = 0
RED_PACKET_CONFIG_TARGET_EMPLOYEE_1DEGREE = 1
RED_PACKET_CONFIG_TARGET_FANS = 2

# 红包活动类型
RED_PACKET_TYPE_EMPLOYEE_BINDING = 0
RED_PACKET_TYPE_RECOM = 1
RED_PACKET_TYPE_SHARE_CLICK = 2
RED_PACKET_TYPE_SHARE_APPLY = 3

# 职位的红包活动状态
HB_STATUS_NONE = 0
HB_STATUS_CLICK = 1
HB_STATUS_APPLY = 2
HB_STATUS_BOTH = 3

# 红包活动状态
HB_CONFIG_FINISHED = 5
HB_CONFIG_RUNNING = 3

# 红包活动调用方式
HB_TRIGGER_WAY_CLICK = 1
HB_TRIGGER_WAY_APPLY = 2

# 发送消息模板的系统模板库常量
TEMPLATES = ObjectDict()
TEMPLATES.RP_EMPLOYEE_BINDING = 44
TEMPLATES.RP_RECOM = 9
TEMPLATES.RP_SHARE = 25
TEMPLATES.POSITION_VIEWED = 25 # 职位被查阅通知
TEMPLATES.APPLY_NOTICE_TPL = 3  # 微信简历投递反馈通知
TEMPLATES.NEW_RESUME_TPL = 24 # 新简历通知
TEMPLATES.FAVPOSITION = 47 # 用户感兴趣后通知
TEMPLATES.RECOM_NOTICE_TPL = 21  # 新候选人通知

# 消息模板开关，控制企业号是否开启某种类型的消息模板发送，与TEMPLATES强对应
TEMPLATES_SWITCH = ObjectDict()
TEMPLATES.APPLY_NOTICE_TPL = 29 # 申请成功时 的消息通知ID
TEMPLATES.NEW_RESUME_TPL = 41  # 认证员工转发之后后有人投递简历 的消息通知ID

WX_MESSAGE_TEMPLATE_SEND_TYPE_WEIXIN = 0
WX_MESSAGE_TEMPLATE_SEND_TYPE_EMAIL = 1
WX_MESSAGE_TEMPLATE_SEND_TYPE_SMS = 2

# ============= 红包相关常量结束 =============

# 常量 Parent code
CONSTANT_PARENT_CODE = ObjectDict(
    COMPANY_TYPE=1101,  # 公司类型
    COMPANY_SCALE=1102,  # 公司规模
    COMPANY_PROPERTY=1103,  # 公司性质
    DEGREE_POSITION=2101,  # 公司职位要求学历
    GENDER_POSITION=2102,  # 性别
    JOB_TYPE=2103,  # 工作性质
    EMPLOYMENT_TYPE=2104,  # 招聘类型
    PRIVACY_POLICY=3101,  # 隐私策略
    WORK_STATUS=3102,  # 工作状态
    POLITIC_STATUS=3103,  # 政治面貌
    DEGREE_USER=3104,  # 用户学历
    WORK_INTENTION=3105,  # 求职意愿-工作类型
    TIME_TO_BE_ON_BOARD=3106,  # 到岗时间
    WORKDAYS_PER_WEEK=3107,  # 每周到岗时间
    LANGUAGE_FRUENCY=3108,  # 语言能力-掌握程度
    GENDER_USER=3109,  # 性别
    MARRIAGE_STATUS=3110,  # 婚姻情况
    ID_TYPE=3111,  # 证件类型
    RECIDENCE_TYPE=3112,  # 户口类型
    MAJOR_RANK=3113,  # 专业排名
    CURRENT_SALARY_MONTH=3114,  # 当前月薪
    CURRENT_SALARY_YEAR=3115,  # 当前年薪
    CAN_ON_SITE=3116,  # 是否接受出差
    WORK_ROTATION=3117,  # 选择班次
    PROFILE_IMPORT_SOURCE=3118,  # Profile来源
    PROFILE_SOURCE=3119,  # Profile创建来源
    REGISTER_SOURCE=4101,  # 用户注册来源(source)
)
