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
import enum

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
WX_USER_SOURCE_IWANTYOU = 12  # 微信端我也要招人注册

WX_USER_SUBSCRIBED = 1
WX_USER_UNSUBSCRIBED = 0

# 环境
ENV = "new_wechat"
ENV_PLATFORM = "platform"
ENV_QX = "qx"
ENV_HELP = "helper"

ROUTE_PREFIX = {
    ENV_PLATFORM: "/m",
    ENV_QX: "/recruit",
    ENV_HELP: "/h"
}

"""appid for infra"""
APPID = {
    ENV_QX: "5",
    ENV_PLATFORM: "6",
    ENV_HELP: "7"
}

# 微信客户端类型
CLIENT_WECHAT = 1
CLIENT_NON_WECHAT = 2
CLIENT_JOYWOK = 3
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
PROFILE_PREVIEW = "预览个人档案"
PROFIEL_VIEW = "个人信息"
PAGE_AI_EMPLOYEE_SURVEY = "填写信息"
PAGE_CAPTCHA = "验证码"
PAGE_JOYWOK_AUTO_BIND = "授权认证"
PAGE_VERIFICATION = "员工认证"
PAGE_EN_VERIFICATION = "Verification"

# 国际化
PAGE_COMPANY_INFO_LOCALE = 'jd_title_dull'
UNTIL_NOW = "until_now"
TO = "to"

# ++++++++++REDIS KEYS++++++++
SESSION_USER = "SESSION_USER_{0}_{1}"
SESSION_ID = "{0}:{1}"
# hr帐号的 session key
SESSION_USER_HR_ACCOUNT = 'user_hr_account_{}'
# hr平台绑定微信后的 pub/sub key
SESSION_WX_BINDING = 'wx_binding_{}'
# Email投递创建Redis格式(邮件解析, 提醒脚本都会用到)
FORMAT_EMAIL_CREATE = "EMAIL_CREATE:{}"  #
# C端用户监听频道
CHAT_CHATROOM_CHANNEL = "chatroom_{0}_{1}"
# HR聊天监听频道
CHAT_HR_CHANNEL = "chatroom_{0}"
# 进入聊天室标志位
CHAT_CHATROOM_ENTER = "chat_sysuser_{}"
# 推荐上传简历
UPLOAD_RECOM_PROFILE = "upload_recom_profile_{}"
# 推荐成功页面手机号码
CONFIRM_REFERRAL_MOBILE = "referral_mobile_{}_{}"
# 模板消息推送完成事件msgid
TEMPLATE_JOB_SEND_FINISH_MSGID = "template_message_receipt_id"
# joywok绑定授权验证码
JOYWOK_IDENTIFY_CODE = "joywok_identify_{}"

# ++++++++++业务常量+++++++++++
# Cookie name
COOKIE_SESSIONID = "5MA8A989"
COOKIE_MVIEWERID = "mviewer_id"
COOKIE_CODE = "JKKSDF89"
COOKIE_DEBUG_AUTH = "cda"
COOKIE_MOBILE_CODE = "ER2T45YU"
COOKIE_MOBILE_REGISTER = "E45645YU"
COOKIE_COUNTRY_CODE_REGISTER = "E45645YF"
MVIEWER_ID = "{0}:{1}"

# Cache 相关常量
VIEWER_TYPE_NEW = 1
VIEWER_TYPE_OLD = 0

# API_STATUS
API_SUCCESS = 0
API_FAILURE = 1
API_WARNING = 2

# newinfra api status
NEWINFRA_API_SUCCESS = '0'
NEWINFRA_API_USER_NOT_EXIST = 'US20000'

# 申请来源
REHIRING_SOURCE = '8'  # 老员工回聘

# 入库的申请来源
REHIRING_ORIGIN = 2097152  # 老员工回聘
TRANSFER_ORIGIN = 4194304  # 员工转岗
INVITE_ORIGIN = 524288  # 邀请投递申请
FORWARD_ORIGIN = 1048576  # 员工转发申请

# 通用状态的布尔值
YES = 1
NO = 0

# 老数据库的通用状态
# TODO (yiliang) 要改！
OLD_YES = 0
OLD_NO = 1

# 我感兴趣状态常量
FAV_INTEREST = 2

# 职位相关，主要涉及到职位，职位列表，搜索页
TEAMNAME_CUSTOM_DEFAULT = "团队"

# 招聘类型
CANDIDATE_SOURCE = {
    "0": "common_experienced",
    "1": "common_graduate"
}
CANDIDATE_SOURCE_SEARCH_LOCALE = {
    "社招": "common_experienced",
    "校招": "common_graduate"
}
CANDIDATE_SOURCE_SEARCH = {
    "0": "社招",
    "1": "校招"
}
CANDIDATE_SOURCE_SEARCH_REVERSE = {
    v: k for k, v in CANDIDATE_SOURCE_SEARCH.items()
}

# 工作性质
EMPLOYMENT_TYPE = {
    "0": "common_fulltime",
    "1": "common_parttime",
    "2": "common_contractor",
    "3": "common_intern",
    "9": "common_other"
}
EMPLOYMENT_TYPE_SEARCH_LOCALE = {
    "全职": "common_fulltime",
    "兼职": "common_parttime",
    "合同工": "common_contractor",
    "实习": "common_intern",
    "其他": "common_other"
}
EMPLOYMENT_TYPE_SEARCH = {
    "0": "全职",
    "1": "兼职",
    "2": "合同工",
    "3": "实习",
    "9": "其他"
}
EMPLOYMENT_TYPE_SEARCH_REVERSE = {
    v: k for k, v in EMPLOYMENT_TYPE_SEARCH.items()
}

MANAGEMENT_EXP = {
    "0": "common_need",
    "1": "common_no_need"
}

# 工作状态
WORKSTATE = {
    "0": "未填写",
    "1": "在职，看看新机会",
    "2": "在职，急寻新工作",
    "3": "在职，暂无跳槽打算",
    "4": "离职，正在找工作",
    "5": "应届毕业生"
}

# 职位学历要求
POSITION_DEGREE = {
    "0": "无",
    "1": "大专",
    "2": "本科",
    "3": "硕士",
    "4": "MBA",
    "5": "博士",
    "6": "中专",
    "7": "高中",
    "8": "博士后",
    "9": "初中",
}

# 学历
DEGREE = {
    "0": "",
    "1": "common_degree_college",
    "2": "common_degree_university",
    "3": "common_degree_master",
    "4": "common_degree_mba",
    "5": "common_degree_doctor",
    "6": "common_degree_technical_secondary_school",
    "7": "common_degree_highschool",
    "8": "common_degree_doctor_above",
    "9": "common_degree_middleschool"
}
DEGREE_SEARCH_LOCALE = {
    "大专": "common_degree_college",
    "本科": "common_degree_university",
    "硕士": "common_degree_master",
    "MBA": "common_degree_mba",
    "博士": "common_degree_doctor",
    "中专": "common_degree_technical_secondary_school",
    "高中": "common_degree_highschool",
    "博士后": "common_degree_doctor_above",
    "初中": "common_degree_middleschool"
}
DEGREE_SEARCH_REVERSE = {
    v: k for k, v in DEGREE_SEARCH_LOCALE.items()
}

# 最高学历
HIGHEST_DEGREE = {
    "1": "common_highest_degree_middleschool",
    "2": "common_highest_degree_secondary_school",
    "3": "common_highest_degree_highschool",
    "4": "common_highest_degree_college",
    "5": "common_highest_degree_university",
    "6": "common_highest_degree_master",
    "7": "common_highest_degree_doctor",
    "8": "common_highest_degree_doctor_above",
    "9": "common_highest_degree_other"
}

RELATIONSHIP = {
    "0": "common_relationship_other",
    "1": "common_relationship_ex_superior",
    "2": "common_relationship_ex_subordinate",
    "3": "common_relationship_ex_colleague",
    "4": "common_relationship_alumnus",
    "5": "common_relationship_friend",
}

RELATIONSHIP_SEARCH_LOCALE = {
    "其他": "common_relationship_other",
    "前上级": "common_relationship_ex_superior",
    "前下属": "common_relationship_ex_subordinate",
    "非上下级的前同事关系": "common_relationship_ex_colleague",
    "校友": "common_relationship_alumnus",
    "亲友": "common_relationship_friend",
}

# 内推 推荐进度页面鼓励语做国际化
REFERRAL_ENCOURAGE = {
    "恭喜您通过初筛，好的开始是成功的一半！": "encourage_primary_pass",
    "恭喜您通过面试，胜利就在不远处！": "encourage_pass_interview",
    "欢迎优秀的你加入我们！": "encourage_join_us",
    "您已进入我司人才库，谢谢您的关注！": "encourage_trm",
}

# 高级搜索筛选项
SEARCH_CONDITION = {
    "1": "search_location",
    "2": "search_salary",
    "4": "search_team",
    "5": "search_recruitment_type",
    "6": "search_job_type",
    "7": "search_education level",
    "8": "search_company"
}

# 及以上 工作经验、学历中使用
POSITION_ABOVE = "common_degree_above"

EXPERIENCE_UNIT = "common_year"
EXPERIENCE_UNIT_PLURAL = "common_years"

# 公司相关
SCALE = {
    "0": "",
    "1": "少于15人",
    "2": "15-50人",
    "3": "50-150人",
    "4": "150-500人",
    "5": "500-1000人",
    "6": "1000-5000人",
    "7": "5000-10000人",  # 似乎数据库中没有？ from yiliang
    "8": "10000人以上",  # 似乎数据库中没有？ from yiliang
}

# 红包相关
REDPACKET = {
    0: "employee_verification",
    1: "endorsement",
    2: "share_position",
    3: "referral_application",
    4: "through_screen"
}

# 奖金相关
BONUS = {
    3: "on_board",
    103: "undo_on_board"
}

# 聊天相关
MSG_TYPE = {
    0: "html",
    1: "button_radio",
    2: "cards",
    3: "jobCard",
    4: "citySelect",
    5: "teamSelect",
    6: "redirect",
    7: "jobSelect",
    8: "employeeBind",
    9: "textPlaceholder",
    10: "positionSelect",
    11: "industrySelect",
    12: "satisfaction",
    13: "uploadResume",
    14: "shareReport",
    15: "positionSubscribe",
}

# 积分配置类型
REWARD_VERIFICATION = "完成员工认证"
REWARD_CLICK_JOB = "转发职位被点击"
REWARD_CONTACT_INFORMATION = "完善被推荐人信息"
REWARD_SUBMIT_PROFILE = "被推荐人投递简历"
REWARD_PASS_REVIEW = "简历评审合格"
REWARD_PASS_INTERVIEW = "面试通过"
REWARD_ON_BOARD = "入职"
REWARD_UPLOAD_PROFILE = "员工上传人才简历"

# 操作的聊天类型
INTERACTIVE_MSG = ["employeeBind", "jobSelect", "teamSelect", "citySelect", "jobCard", "positionSelect", "industrySelect", "uploadResume", "shareReport", "positionSubscribe"]

# 默认图标
SYSUSER_HEADIMG = "weixin/images/hr-avatar-default.png"
HR_HEADIMG = "weixin/images/default-HR.png"
COMPANY_HEADIMG = "common/images/default-company-logo.jpg"

# 招聘进度全状态 （tangyiliang）
# cofnigdb.config_sys_points_conf_tpl.id
# (对应hrdb.hr_points_conf 中 template_id)      ** 表示这是牵涉到加积分的操作
RECRUIT_STATUS_APPLY_ID = 1  # ** 提交简历成功
RECRUIT_STATUS_INTERVIEW_ID = 2  # HR安排面试
RECRUIT_STATUS_HIRED_ID = 3  # ** 入职
RECRUIT_STATUS_REJECT_ID = 4  # 拒绝
RECRUIT_STATUS_INTERVIEWPENDING_ID = 5  # MGR面试后表示先等待
RECRUIT_STATUS_CVCHECKED_ID = 6  # 简历被查看
RECRUIT_STATUS_RECOMCLICK_ID = 7  # ** 转发被点击
RECRUIT_STATUS_CVFORWARDED_ID = 8  # 转发简历MGR评审
RECRUIT_STATUS_CVPENDING_ID = 9  # MGR评审后表示先等待
RECRUIT_STATUS_CVPASSED_ID = 10  # 评审通过要求面试
RECRUIT_STATUS_OFFERACCEPTED_ID = 11  # 接受录取通知
RECRUIT_STATUS_OFFERED_ID = 12  # ** 发出录取通知
RECRUIT_STATUS_FULL_RECOM_INFO_ID = 13  # ** 完善被推荐人
RECRUIT_STATUS_VERIFICATION = 14  # 员工认证
RECRUIT_STATUS_UPLOAD_RESUME = 15  # 简历上传

# 职位在招状态
POSITION_STATUS_RECRUITING = 0  # 有效
POSITION_STATUS_DELETED = 1  # 删除
POSITION_STATUS_WITHDRAWN = 2  # 撤下

# 职位状态
RP_POSITION_STATUS_NONE = 0
RP_POSITION_STATUS_CLICK = 1
RP_POSITION_STATUS_APPLY = 2
RP_POSITION_STATUS_BOTH = 3
RP_POSITION_STATUS_SCREEN = 4
# 国际编码列表
NATIONAL_CODE = [
    {'id': 1, 'code': '+86', 'country': '中国'}
]

MOBILE_CODE_OPT_TYPE = ObjectDict({
    'code_register': 1,
    'forget_password': 2,
    'valid_old_mobile': 3,
    'change_mobile': 4,
    'referral_confirm': 5
})

# 简历导入
RESUME_WAY_MOSEEKER_PC = "0"
RESUME_WAY_MOSEEKER = "1"
RESUME_WAY_51JOB = "2"
RESUME_WAY_LIEPIN = "3"
RESUME_WAY_ZHILIAN = "4"
RESUME_WAY_LINKEDIN = "5"
RESUME_WAY_VERYEAST = "6"
RESUME_WAY_30S = "7"

RESUME_WAY_SPIDER = {
    RESUME_WAY_51JOB: "51job.html",
    RESUME_WAY_ZHILIAN: "zhaopin.html",
    RESUME_WAY_LIEPIN: "liepin.html",
    RESUME_WAY_VERYEAST: "veryeast.html",
    RESUME_WAY_LINKEDIN: "linkedin.html"
}

RESUME_WAY_TO_INFRA = {
    RESUME_WAY_51JOB: 1,
    RESUME_WAY_LIEPIN: 2,
    RESUME_WAY_ZHILIAN: 3,
    RESUME_WAY_LINKEDIN: 4,
    RESUME_WAY_VERYEAST: 6
}

# 新JD公司hr_cms_pages.type
CMS_PAGES_TYPE_COMPANY_INDEX = 1
CMS_PAGES_TYPE_TEAM_DETAIL = 2
CMS_PAGES_TYPE_POSITION_DETAIL = 3

# 新JD状态
NEWJD_STATUS_NO_TEMPTED = 0  # 未开启
NEWJD_STATUS_WAITING = 1  # 用户开启, 等待审核
NEWJD_STATUS_ON = 2  # 开启
NEWJD_STATUS_OFF = 3  # 撤销

# 新JD模块类型
CMS_PAGES_MODULE_A = 1
CMS_PAGES_MODULE_B = 2
CMS_PAGES_MODULE_C = 3
CMS_PAGES_MODULE_D = 4
CMS_PAGES_MODULE_E = 5
CMS_PAGES_MODULE_MAP = 6
CMS_PAGES_MODULE_QRCODE = 7
CMS_PAGES_MODULE_TEAM_DETAIL = 8
CMS_PAGES_MODULE_POSITION_DETAIL = 9

# 新JD Resources类型
CMS_PAGES_RESOURCES_TYPE_IMAGE = 0
CMS_PAGES_RESOURCES_TYPE_VIDEO = 1

# ============= 红包相关常量 =============
# 红包锁字符串模版
RP_POS_LOCK_FMT = "rplock_pos:%s:%s:%s"
RP_EMP_LOCK_FMT = "rplock_emp:%s:%s"
RP_RECOM_LOCK_FMT = "rplock_recom:%s:%s"
ON_BOARD_LOCK_FMT = "rplock_on_board:%s:%s"
RP_LOCKED = 1

# 红包mq name
CLICK_MQ_NAME = "retransmit click"
APPLY_MQ_NAME = "retransmit apply"

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
RED_PACKET_TYPE_SCREEN = 4

# 刮刮卡状态
SRRATCH_CARD_INTACT = 0
SRRATCH_CARD_OPENED = 1

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
HB_TRIGGER_WAY_SCREEN = 3

# 红包活动的索引值
HB_INDEX_CLICK = 0
HB_INDEX_APPLY = 1
HB_INDEX_SCREEN = 2

# 红包类型
HB_CONFIG_TYPR_TO_INDEX = {
    2: 0,  # 转发被点击
    3: 1,  # 转发被申请
    4: 2   # 推荐通过初筛
}

# 红包类型对应的红包状态值
HB_CONFIG_TYPR_TO_HB_STATUS = {
    2: 1,  # 转发被点击
    3: 2,  # 转发被申请
    4: 4   # 推荐通过初筛
}


# 发送消息模板的系统模板库常量
TEMPLATE_URL_SUFFIX = "&from_template_message={}&send_time={}"
TEMPLATE_URL_SUFFIX_ = "?from_template_message={}&send_time={}"
TEMPLATES = ObjectDict()
TEMPLATES.RP_EMPLOYEE_BINDING = 49
TEMPLATES.RP_RECOM = 68
TEMPLATES.RP_SHARE = 43
TEMPLATES.POSITION_VIEWED = 25  # 职位被查阅通知
TEMPLATES.NEW_RESUME_TPL = 24  # 新简历通知
TEMPLATES.FAVPOSITION = 47  # 用户感兴趣后通知
TEMPLATES.RECOM_NOTICE_TPL = 67  # 新候选人通知
TEMPLATES.REFINE_EMPLOYEE_INFO_TPL = 44  # 员工认证自定义字段填写通知
TEMPLATES.POSITION_VIEWED_SHARED = 39
TEMPLATES.POSITION_VIEWED_FIVE_TIMES = 63
TEMPLATES.RP_SCREEN = 82
TEMPLATES.WX_RANKING_NOTICE_TO_EMPLOYEE = 78  # 积分排行榜 - 给员工
TEMPLATES.APPLICATION_INVITE = 85  # 投递邀请

# 消息模板开关，控制企业号是否开启某种类型的消息模板发送，与TEMPLATES强对应
TEMPLATES_SWITCH = ObjectDict()
TEMPLATES_SWITCH.REFINE_EMPLOYEE_INFO_TPL = 44  # 员工认证自定义字段填写通知
TEMPLATES_SWITCH.JD_SCAN_FIVE_TIME = 63

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
    INDUSTRY=3124,  # 期望行业
    REGISTER_SOURCE=4101,  # 用户注册来源(source)
    CONTINENT=9103,  # 大洲
    ROCKETMAJOR_L1=990000,  # 火箭一级专业
    REFERRAL_RELATIONSHIP=3135,    # 被推荐人与内推人的关系
)

# hr_employee_cert_conf.auth_mode 的数据库枚举值
EMPLOYEE_BIND_AUTH_MODE = ObjectDict(
    DISABLE=0,
    EMAIL=1,
    CUSTOM=2,
    EMAIL_OR_CUSTOM=4,
    QUESTION=5,
    EMAIL_OR_QUESTION=6,
    WORKWX=7
)

# user_employee.auth_method 的数据库枚举值
USER_EMPLOYEE_AUTH_METHOD = ObjectDict(
    EMAIL=0,
    CUSTOM=1,
    QUESTION=2,
    WORKWX=3
)

# 员工认证状态码
# 和基础服务返回的状态码一致
EMPLOYEE_BIND_STATUS_BINDED = 0
EMPLOYEE_BIND_STATUS_UNBINDING = 1
EMPLOYEE_BIND_STATUS_EMAIL_PENDING = 2

# 员工添加积分类型
EMPLOYEE_AWARD_TYPE_DEFAULT_ERROR = 0
EMPLOYEE_AWARD_TYPE_SHARE_CLICK = 1
EMPLOYEE_AWARD_TYPE_SHARE_APPLY = 2
EMPLOYEE_AWARD_TYPE_RECOM = 3

# 1:微信企业端(正常), 2:微信企业端(我要投递), 3:微信企业端(我感兴趣),
# 4:微信聚合端(正常), 5:微信聚合端(我要投递), 6:微信聚合端(我感兴趣),
# 8:移动网页端(正常), 9:移动网页端(我要投递)
# 100:微信企业端Email申请, 101:微信聚合端Email申请,
# 150:微信企业端导入, 151:微信聚合端导入, 152:PC导入, 153:移动网页端导入
# 200:PC(正常添加) 201:PC(我要投递) 202: PC(我感兴趣)',
PROFILE_SOURCE_PLATFORM = 1
PROFILE_SOURCE_PLATFORM_APPLY = 2
PROFILE_SOURCE_PLATFORM_INTEREST = 3
PROFILE_SOURCE_QX = 4
PROFILE_SOURCE_QX_INTEREST = 6
PROFILE_SOURCE_MOBILE_BROWSER = 8

INFRA_ERROR_CODES = [1, -1, 99999]

# mandrill
MANDRILL_EMAIL_HEADER_LIMIT = 50

# mandrill template_name
KA_EMAIL_APPLICATION_INVITATION = "ka-email-application-invitation"
NON_KA_EMAIL_APPLICATION_INVITATION = "non-ka-email-application-invitation"

EMPLOYEE_CUSTOM_FIELD_REFINE_REDIRECT = 1
EMPLOYEE_CUSTOM_FIELD_REFINE_TEMPLATE_MSG = 2

# chatbot
CHAT_SPEAKER_USER = 0
CHAT_SPEAKER_HR = 1
CHAT_SPEAKER_BOT = 2
# origin
ORIGIN_USER_OR_HR = 0
ORIGIN_WELCOME = 1
ORIGIN_CHATBOT = 2

COMPANY_CONF_CHAT_OFF = 0
COMPANY_CONF_CHAT_ON = 1
COMPANY_CONF_CHAT_ON_WITH_CHATBOT = 2

FRONT_TYPE_FIELD_TEXT = 0
FRONT_TYPE_FIELD_TEXTAREA = 1
FRONT_TYPE_FIELD_SELECT_NARMOL = 10
FRONT_TYPE_FIELD_SELCET_POPUP = 13

# 简历导入渠道
FROM_MAIMAI = 1
FROM_LIEPIN = 2


LIEPIN_SCENE_KEY_FMT = 'liepin_auth_scene_params:{sysuser_id}'
LIEPIN_SCENE_KEY_TTL = 30 * 24 * 60 * 60

# Mars公司id
MARS_ID = 345

# 积分排行榜
PAGE_FROM_ONE = 1
PAGE_SIZE_FIVE = 5

# 内推候选人 关闭弹层
REFERRAL_CLOSE_QRCODE = 0
REFERRAL_CLOSE_PROFILE = 1

# 榜单类型
LADDER_TYPE = {"month": "1",
               "quarter": "2",
               "year": "3"}

# 临时二维码场景值
QRCODE_BIND = 1  # 员工认证
QRCODE_POLICY = 2  # 内推政策
QRCODE_LADDER = 3  # 积分榜单
QRCODE_AWARD_RECORD = 4  # 积分历史
QRCODE_RECOM_RECORD = 5  # 推荐历史
QRCODE_REFERRED_FRIENDS = 6  # 候选人推荐
QRCODE_USERCENTER = 7  # 个人中心
QRCODE_MINE = 8  # 我的
QRCODE_REFERRAL_PROFILE = 9  # 推荐人才简历
QRCODE_REFERRAL_KETINFO = 10  # 推荐人才关键信息
QRCODE_POSITION_INFO = 11  # 职位列表
QRCODE_REFERRAL_CONFIRM = 12  # 用户认领推荐成功
QRCODE_SCAN_REFERRAL = 13  # 浏览候选人推荐职位
QRCODE_POSITION = 14  # 职位详情
QRCODE_SIDEBAR = 15  # 侧边栏二维码
QRCODE_OTHER = 99  # 默认

# 临时二维码字符串参数
TEMPORARY_CODE_STR_SCENE = "{}_{}"

# 临时二维码字符串参数的场景值
STR_SCENE_JOYWOK = "JOYWOK"

# mq相关常量
EXCHANGE_TYPE = 'topic'
DURABLE = True
REDPACKET_EXCHANGE = "redpacket_exchange"
REDPACKET_QUEUE = "redpacket_queue"
MQ_REDPACKET_ROUTING_KEY = "*.red_packet"

SCREEN_RP_TYPE = "screen"
EMPLOYEE_BIND_RP_TYPE = "employee_bind"


# 二维码关注来源
QRCODE_FROM_POSITION_POPUP = 1


# 格力引导的职位链接
GELI_COMPANY_ID = 1730310
GELI_WEBSITE = 'http://gree.zhiye.com'
GELI_POSITION_URL = 'http://gree.zhiye.com/zpdetail/{}'

# 开启了员工内部转岗功能的公司
TRANSFER_COMPANY_ID = [2052173, 601320]

# 内推：员工推荐评价入口
REFERRAL_EVAL_CONTACT_MES_TMP = 1    # 候选人联系内推消息模板
REFERRAL_EVAL_RADAR = 2              # 人脉雷达
REFERRAL_EVAL_RECOM_PROGRESS = 3     # 推荐进度列表
REFERRAL_EVAL_TEN_MIN_MES_TMP = 4    # 十分钟消息推送模板
REFERRAL_EVAL_SEEK_RECOM_CARDS = 5   # 求推荐分类统计卡

REFERRAL_EXPIRED_MESSAGE = 'expired_message'

# 人脉连连看  连接状态
CONNECTION_ING = 2
CONNECTION_COMPLETED = 1

# JD补充简历
PROMOTE = '1'

# chatbot推荐职位
FANS_RECOMMEND = '2'
EMPLOYEE_RECOMMEND = '4'

# 神策cookie
SENSORS_COOKIE = 'sensorsdata2015jssdkcross'

# 神策来源
SA_ORIGIN_FANS_RECOMMEND = 1  # 粉丝转发
SA_ORIGIN_EMPLOYEE_SHARE = 2  # 员工转发
SA_ORIGIN_PLATFORM = 3  # 公众号
SA_ORIGIN_RANKING_TEMPLATE = 4  # 推送排名榜单
SA_ORIGIN_PORTAL = 5  # 员工portal
SA_ORIGIN_APPLICATION_INVITE = 6  # 投递邀请
SA_ORIGIN_PROMOTE = 7  # JD页补充简历

# 请求jmis的方法
JMIS_SIGNATURE = "getSignature"
JMIS_USER_INFO = "getUserInfo"

MAIDANGLAO_COMPANY_ID = 133445
MAIDANGLAO_WECHAT_ID = 414
JOYWOK_EXCEPTION_CODE = (42061, 42062, 42063)

# 神策推荐来源
# 直接推荐
SA_DIRECT_REFERRAL_ORIGIN_WECHAT_UPLOAD = 5  # 微信上传
SA_DIRECT_REFERRAL_ORIGIN_PHONE_UPLOAD = 6  # 手机本地上传
SA_DIRECT_REFERRAL_ORIGIN_PC_UPLOAD = 7  # PC上传
SA_DIRECT_REFERRAL_ORIGIN_REFERRAL_CRUCIAL_INFO = 8  # 推荐关键信息
# 间接评价
SA_INDIRECT_REFERRAL_REFERRAL = 1  # 联系内推
SA_INDIRECT_REFERRAL_INVITE = 2  # 邀请投递
SA_INDIRECT_REFERRAL_TRANSFER = 3  # 转发投递
# 推荐评价
SA_REFERRAL_COMMENT_ORIGIN_CONTACT_MES_TMP = "候选人联系内推消息模板"
SA_REFERRAL_COMMENT_ORIGIN_RADAR = "人脉雷达"
SA_REFERRAL_COMMENT_ORIGIN_PROGRESS = "推荐进度列表"
SA_REFERRAL_COMMENT_ORIGIN_TEN_MIN_MES_TMP = "十分钟消息推送模板"
SA_REFERRAL_COMMENT_ORIGIN_SEEK_RECOM_CARDS = "求推荐分类统计卡"
SA_REFERRAL_COMMENT_ORIGIN_HAS_APPLY = "已投递"

# 语言
LOCALE_ENGLISH = 'en_US'
LOCALE_CHINESE = 'zh_CN'
