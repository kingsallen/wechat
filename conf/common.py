# coding=utf-8

'''
说明:
constant配置常量规范：
1.常量涉及通用业务逻辑定义，即同时适用于聚合号和企业号
2.系统常量定义在顶部，业务常量定义在底部。
3.使用分割线区分系统、业务常量
4.常量配置添加注释

常量使用大写字母，字符串需要时标注为unicode编码
例如 SUCCESS = u"成功"

'''

# ++++++++++系统常量++++++++++

## 返回错误

## status_code默认错误返回
RESPONSE_SUCCESS = u"success"
RESPONSE_FAILED = u"failed"

## 环境
ENV_PLATFORM = u"platform"
ENV_QX = u"qx"
ENV_HELP = u"help"

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

## 职位相关，主要涉及到职位，职位列表，搜索页
### 招聘类型
CANDIDATE_SOURCE = {
    "0": u"社招",
    "1": u"校招",
}

### 工作性质
EMPLOYMENT_TYPE = {
    "0": u"全职",
    "1": u"兼职",
    "2": u"合同工",
    "3": u"实习",
}

### 学历
DEGREE = {
    "1": u"大专",
    "2": u"本科",
    "3": u"硕士",
    "4": u"MBA",
    "5": u"博士",
    "6": u"中专",
    "7": u"高中",
    "8": u"博士后",
    "9": u"初中"
}

### 及以上 工作经验、学历中使用
POSITION_ABOVE = u"及以上"
EXPERIENCE_UNIT = u"年"
