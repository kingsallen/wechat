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

# 注册来源
WECHAT_REGISTER_SOURCE_QX = 1
WECHAT_REGISTER_SOURCE_PLATFORM = 2
WXUSER_OAUTH_UPDATE = 7
WXUSER_OAUTH = 4

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

# ++++++++++REDIS KEYS++++++++
SESSION_USER = "SESSION_USER_{0}_{1}"
SESSION_ID = "{0}:{1}"


# ++++++++++业务常量+++++++++++
# Cookie name
COOKIE_SESSIONID = "5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8"
COOKIE_CODE = "JKKSDF89H43HIDJJ0NNBS17YH8O35321DGAF8655KKDWTYE082L1711209AAUC54"

# Cache 相关常量
VIEWER_TYPE_NEW = 1
VIEWER_TYPE_OLD = 0

# API_STATUS
API_SUCCESS = 0
API_FAILURE = 1

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


# 红包
# 职位状态
RP_POSITION_STATUS_NONE = 0
RP_POSITION_STATUS_CLICK = 1
RP_POSITION_STATUS_APPLY = 2
RP_POSITION_STATUS_BOTH = 3

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

#红包活动状态
HB_CONFIG_FINISHED = 5
HB_CONFIG_RUNNING = 3

#红包活动调用方式
HB_TRIGGER_WAY_CLICK = 1
HB_TRIGGER_WAY_APPLY = 2

# 发送消息模板的系统模板库常量
TEMPLATES = ObjectDict()
TEMPLATES.RP_EMPLOYEE_BINDING = 44
TEMPLATES.RP_RECOM = 9
TEMPLATES.RP_SHARE = 25
TEMPLATES.POSITION_VIEWED = 25 # 职位被查阅通知

WX_MESSAGE_TEMPLATE_SEND_TYPE_WEIXIN = 0
WX_MESSAGE_TEMPLATE_SEND_TYPE_EMAIL = 1
WX_MESSAGE_TEMPLATE_SEND_TYPE_SMS = 2

SEND_RP_REQUEST_FORMAT = """
<xml>
<sign><![CDATA[{sign}]]></sign>
<mch_billno><![CDATA[{mch_billno}]]></mch_billno>
<mch_id><![CDATA[{mch_id}]]></mch_id>
<wxappid><![CDATA[{wxappid}]]></wxappid>
<send_name><![CDATA[{send_name}]]></send_name>
<re_openid><![CDATA[{re_openid}]]></re_openid>
<total_amount><![CDATA[{total_amount}]]></total_amount>
<total_num><![CDATA[{total_num}]]></total_num>
<wishing><![CDATA[{wishing}]]></wishing>
<client_ip><![CDATA[{client_ip}]]></client_ip>
<act_name><![CDATA[{act_name}]]></act_name>
<remark><![CDATA[{remark}]]></remark>
<nonce_str><![CDATA[{nonce_str}]]></nonce_str>
</xml>
"""
