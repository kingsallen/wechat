# coding=utf-8

# Copyright 2016 MoSeeker

"""
时间工具类
"""
import time
from datetime import datetime, timedelta

import conf.common as constant


def curr_datetime_now():
    return datetime.now()


def curr_now() -> str:
    return datetime.now().strftime(constant.TIME_FORMAT)


def curr_now_pure():
    return datetime.now().strftime(constant.TIME_FORMAT_PURE)


def curr_now_dateonly():
    return datetime.now().strftime(constant.TIME_FORMAT_DATEONLY)


def curr_now_minute():
    return datetime.now().strftime(constant.TIME_FORMAT_MINUTE)


def curr_now_msec():
    return datetime.now().strftime(constant.TIME_FORMAT_MSEC)


def format_dateonly(time):
    return time.strftime(constant.TIME_FORMAT_DATEONLY)


def curr_now_ts(precision='s'):
    """
    当前系统时间时间戳
    :param precision 精度：默认为s即十位时间戳,f为13位时间戳
    """
    if precision == 'f':
        return int(time.time())
    else:
        return int(time.time()*1000)


def subtract_design_time_ts(ts=None, minutes=None) -> int:
    """
    减去指定时间的时间戳
    :param ts 没有时为当前系统10位时间戳，
    :param minutes 减去的分钟数
    :return 13位长度的时间戳
    """
    if ts is None:
        ts = curr_now_ts()
    if minutes:
        # 转换成localtime
        time_local = time.localtime(ts)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        dt = datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time_local), "%Y-%m-%d %H:%M:%S") - timedelta(minutes=minutes)

        res_ts = time.mktime(time.strptime(str(dt), '%Y-%m-%d %H:%M:%S')) * 1000
        return res_ts


def is_time_valid(str_time, form):
    """
    判断时间格式是否符合要求
    """
    ret = False
    try:
        if datetime.strptime(str_time, form):
            ret = True
    except ValueError:
        pass
    finally:
        return ret


def str_2_date(str_time, format):
    """
    将字符串时间格式转化为 datetime
    :param str_time:
    :param form:
    :return:
    """
    res_date_time = str_time
    try:
        res_date_time = datetime.strptime(str(str_time), format)
    except ValueError:
        res_date_time = datetime.strptime(str(str_time), constant.TIME_FORMAT)
        res_date_time = res_date_time.strftime(format)
    finally:
        return res_date_time


def jd_update_date(update_time):
    """
    JD以及列表页根据规则显示更新时间
    :param update_time: datetime类型
    :return:
    """

    update_date = constant.JD_TIME_FORMAT_DEFAULT
    try:
        if update_time:
            # 2016-11-23
            update_date = constant.JD_TIME_FORMAT_FULL.format(
                update_time.year, update_time.month, update_time.day)

    except Exception as e:
        pass
    finally:
        return update_date


if __name__ == "__main__":
    print(str_2_date("2017-03-13 16:39:35", "%Y-%m-%d %H:%M"))
