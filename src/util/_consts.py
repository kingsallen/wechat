# coding=utf-8

# session.py
REDIS_HOST_KEY = u"redis_host"
REDIS_PORT_KEY = u"redis_port"
REDIS_PASS_KEY = u"redis_pass"

COOKIE_SESSION_KEY = u"session_id"
COOKIE_HMAC_KEY = u"verification"

SESSION_INDEX_ERROR = u"session index error"

# datetool.py
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
