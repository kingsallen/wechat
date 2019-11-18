# coding=utf-8

# status_message
RESPONSE_SUCCESS = "SUCCESS"
RESPONSE_WARNING = "WARNING"
RESPONSE_FAILURE = "FAILURE"

BACK_CN = "返回"
LOGIN_FAILURE = "登录失败"
OPERATE_FAILURE = "操作失败"
MOBILE_VERIFY = "请先验证手机号"
INPUT_DISORDER = "请按规范输入"
PREVIEW_PROFILE = "继续填写个人档案"
DEFAULT_ERROR_MESSAGE = ['系统异常，请稍后再试']

BASIC_SERVER_DISCONNECTION = "基础服务器连接不上"
BASIC_SERVER_BUSY = "基础服务器忙碌"

CELLPHONE_BIND = "用户已绑定手机号"
CELLPHONE_UNBIND = "用户未绑定手机号"
CELLPHONE_INVALID_CODE = "验证码不正确"
CELLPHONE_INVALID_MOBILE = "该手机号不存在"
CELLPHONE_MOBILE_HAD_REGISTERED = "该手机号已被注册"
CELLPHONE_MOBILE_SET_PASSWD_FAILED = "设置密码无效，请重新验证手机号"
CELLPHONE_REGISTER_PASSWD_NOT_MATCH = "两次输入密码不一致，请重新设置"
CELLPHONE_REGISTER_FAILED = "用户注册失败"
CELLPHONE_RESET_PASSWORD = "设置密码失败，请重试"
CELLPHONE_PASSWORD_ERROR = "密码要求为至少六位以上的数字与字母组合"
CELLPHONE_NOT_MATCH = "输入的手机号与原绑定手机号不一致"
CELLPHONE_NAME_EMAIL = "姓名或者邮箱格式错误"
CELLPHONE_MOBILE_INVALID = "手机号未提供或未验证"

VCODE_NOT_EXIST = "验证码不存在"
VCODE_INVALID = "验证码错误"

RESUME_IMPORT_NAME_PASSWD_ERROR = "用户名和密码必须填写"
RESUME_IMPORT_SUCCESS = "导入成功"
RESUME_IMPORT_FAILED = "导入失败"

CAPTCHA_SUCCESS = ["已提交验证"]

DATABASE_ERROR = "数据库操作失败"

REQUEST_PARAM_ERROR = "请求参数错误"

NOT_AUTHORIZED = "用户未被授权请求"
NO_DATA = "404!Ta在地球上消失了"
UNKNOWN_DEFAULT = "系统维护中"

POSITION_FORWARD_MESSAGE = "点击右上角\n将职位推送给朋友,\n或者直接分享到朋友圈吧!"
SHARE_DES_DEFAULT = "share_des_default"

RED_PACKET_TYPE_VALUE_ERROR = "红包配置类型错误!"
RED_PACKET_CONFIG_TARGET_VALUE_ERROR = "红包配置对象错误!"
RED_PACKET_WISHING = "红包一个，聊表心意，祝君好运"
RED_PACKET_HEADLINE = "抽中了!"
RED_PACKET_HEADLINE_FAILURE = "很遗憾,没有摸到"

WECHAT_SCAN_HAD_BINDED = "当前扫描微信号已经绑定其他帐号了, 请更换微信号重新扫描"
WECHAT_SCAN_FAILED = "绑定失败, 请尝试先解绑微信号"
WECHAT_SCAN_CHANGE_WECHAT = "当前扫描微信号不是已绑定微信号, 请使用正确的微信号进行扫描"

POSITION_NOT_EXIST = "您访问的职位不存在"
POSITION_ALREADY_EXPIRED = "您申请的职位已经过期"
DUPLICATE_APPLICATION = "您已申请过该职位，请在个人中心查询您的申请详情"
CREATE_APPLICATION_FAILED = ["您的申请失败了，请稍候再试"]

PROFILE_COMPANY_NAME_EXISTED = "该企业已存在，可返回选择"
PROFILE_REQUIRED_HINT_HEAD = "请完善个人简历，其中"
PROFILE_REQUIRED_HINT_TAIL = "为必填项"
PROFILE_OVERLENGTH = "%s内容长度过长"
PROFILE_IMPORT_LIMIT = ["您今天已尝试导入超过三次", "请明天再试"]

# 招聘助手
HELPER_HR_REGISTERED = "您的账户已存在，请联系管理员"
HELPER_COMPANY_REGISTERED = "该公司名称已注册"
HELPER_HR_REGISTERED_FAILED = "注册失败"
HELPER_HR_HAD_REGISTERED = "手机号已经注册，请勿重复注册"

EMPLOYEE_BINDING_SUCCESS = "employee_verification_success"
EMPLOYEE_BINDING_FAILURE_INFRA = "员工认证信息不正确"
EMPLOYEE_BINDING_FAILURE = "employee_incorrect_info"
EMPLOYEE_BINDING_CUSTOM_FIELDS_DONE = "{}信息提交成功!"

EMPLOYEE_BINDING_FAILURE_EMAIL_OCCUPIED_INFRA = "该邮箱已被认证"
EMPLOYEE_BINDING_FAILURE_EMAIL_OCCUPIED = "employee_binding_failure_email_occupied"

EMPLOYEE_BINDING_EMAIL_DONE0 = "employee_revification_email_done0"
EMPLOYEE_BINDING_EMAIL_DONE1 = "employee_revification_email_done1"

EMPLOYEE_BINDING_EMAIL_BTN_TEXT = "employee_revification_i_see"
EMPLOYEE_BINDING_DEFAULT_BTN_TEXT = "去转发职位"
EMPLOYEE_AWARDS_LADDER_SHARE_TEXT = "{}的伯乐排行榜放榜啦！"
EMPLOYEE_AWARDS_LADDER_DESC_TEXT = "快来看看你在人脉圈的地位"

CREDIT_MALL_SHARE_TITLE = '{}积分商城'
CREDIT_MALL_SHARE_TEXT = '邀您兑好礼'
MALL_GOOD_DETAIL_SHARE_TITLE = '我在用积分兑换{}'
MALL_GOOD_DETAIL_SHARE_TEXT = '快去赚积分换好礼'


EMPLOYEE_NOT_BINDED_WARNING = "请先进行{}绑定"
EMPLOYEE_BINDED_WARNING = "该{}已经绑定"

DEFAULT_RECOMMEND_PRESENTEE = "请帮您的好友们做个推荐吧！\n他们很希望能成为您的同事"
DEFAULT_RECOMMEND_SUCCESS = "感谢您对公司人才库的贡献"

EMAIL_FMT_FAILURE = "Email格式不正确"

# 人脉连连看链接分享
REFERRAL_CONNECTION_TITLE = '人脉连连看'
REFERRAL_CONNECTION_TEXT = '{}！有朋友喊你看机会！'

# 转发邀请投递分享
REFERRAL_INVITE_TITLE = '诚邀您投递职位'
REFERRAL_INVITE_TEXT = '这是一个千载难逢的内推机会哦~'

# 内推进度页面分享
REFERRAL_PROGRESS_TITLE = '内推进度分享'
REFERRAL_PROGRESS_DESCRIPTION = '快来看看你的应聘进度吧~'

# joywok自动认证
JOYWOK_AUTO_BIND_SUCCESS = "员工认证成功，微信绑定已完成，快去转发职位吧"
JOYWOK_AUTO_BIND_EMPLOYEE_INFO_IS_GONE = "该员工信息已被认证"
JOYWOK_AUTO_BIND_FAIL = "员工认证失败"

# 员工和候选人聊天
CHATTING_EMPLOYEE_RESIGNATION = "对方已不在公司，需要了解职位情况可以找HR或者其他员工沟通哦~"
CHATTING_USER_UNSUBSCRIBE = "对方未关注公众号，暂时无法收到提醒！"
CHATTING_EMPLOYEE_RESIGNATION_TIPS = "员工已不在公司!"
CHATTING_EMPLOYEE_EMPLOYEE_TIPS = "候选人已认证为本公司员工!"
