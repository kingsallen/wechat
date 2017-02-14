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


def curr_now():
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


def jd_update_date(update_time):
    """
    JD以及列表页根据规则显示更新时间
    :param update_time: datetime类型
    :return:
    """

    update_date = constant.JD_TIME_FORMAT_DEFAULT
    try:
        if update_time:
            datetime_now = datetime.now()
            yesterday = datetime_now + timedelta(days=-1)

            delta = datetime_now - update_time

            if datetime_now.date() == update_time.date():
                if delta.seconds <= 3600:
                    # 刚刚（即一个小时内）
                    update_date = constant.JD_TIME_FORMAT_JUST_NOW
                else:
                    # 今天 12：00
                    update_date = constant.JD_TIME_FORMAT_TODAY.format(
                        update_time.hour, update_time.minute)
            elif yesterday.date() == update_time.date():
                # 昨天 12：00
                update_date = constant.JD_TIME_FORMAT_YESTERDAY.format(
                    update_time.hour, update_time.minute)
            else:
                # 2016-11-23
                update_date = constant.JD_TIME_FORMAT_FULL.format(
                    update_time.year, update_time.month, update_time.day)

    except Exception as e:
        pass
    finally:
        return update_date
