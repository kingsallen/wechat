# coding=utf-8

'''
说明:
constant配置常量规范：
1.常量涉及通用业务逻辑定义，即同时适用于聚合号和企业号
2.系统常量定义在顶部，业务常量定义在底部。
3.使用分割线区分系统、业务常量
4.常量配置添加注释
'''

# COOKIE_SESSION_KEY = u"session_id"
# COOKIE_HMAC_KEY = u"verification"
# SESSION_INDEX_ERROR = u"session index error"

# ++++++++++系统常量++++++++++

## 返回错误

### status_code默认错误返回
RESPONSE_SUCCESS = "SUCCESS"
RESPONSE_FAILED = "FAILED"

## 入库字段类型
TYPE_INT = 1
TYPE_JSON = 2
TYPE_FLOAT = 3
TYPE_TIMESTAMP = 4
TYPE_STRING = 5  # 会过滤xss
TYPE_STRING_ORIGIN = 6  # 不过滤xss

## 日期、时间规范
TIME_FORMAT = u"%Y-%m-%d %H:%M:%S"
TIME_FORMAT_PURE = u"%Y%m%d%H%M%S"
TIME_FORMAT_DATEONLY = u"%Y-%m-%d"
TIME_FORMAT_MINUTE = u"%Y-%m-%d %H:%M"
TIME_FORMAT_MSEC = u"%Y-%m-%d %H:%M:%S.%f"
JD_TIME_FORMAT_DEFAULT = u"-"
JD_TIME_FORMAT_FULL = u"{0}-{:0>2}-{:0>2}"
JD_TIME_FORMAT_JUST_NOW = u"刚刚"
JD_TIME_FORMAT_TODAY = u"今天 {:0>2}:{:0>2}"
JD_TIME_FORMAT_YESTERDAY = u"昨天 {:0>2}:{:0>2}"
JD_TIME_FORMAT_THIS_YEAR = u"{:0>2}-{:0>2}"

## 数据库规范化常量
STATUS_INUSE = 1
STATUS_UNUSE = 0

# ++++++++++业务常量+++++++++++

## 职位相关
### 招聘类型

candidate_source = {
    "0": "社招",
    "1": "校招",
}

### 工作性质
employment_type = {
    "0": "全职",
    "1": "兼职",
    "2": "合同工",
    "3": "实习生",
}

### 学历
degree = {
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

### 及以上 工作经验、学历中使用
position_above = "及以上"
experience_unit = "年"

### 招聘类型
candidate_source = {
    "0": "社招",
    "1": "校招",
}