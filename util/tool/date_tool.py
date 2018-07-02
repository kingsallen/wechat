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
