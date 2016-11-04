# coding=utf-8

# Copyright 2016 MoSeeker

"""
时间工具类
"""

from datetime import datetime, date

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
    :param update_time: timestamp类型
    :return:
    """

    update_date = constant.JD_TIME_FORMAT_DEFAULT
    try:
        if update_time:
            today = date.today()
            datetime_today = datetime(today.year, today.month, today.day, 0,0,0,0)
            datetime_now = datetime.now()

            delta = datetime_now - update_time
            delta_to_today = datetime_now - datetime_today

            if delta.days == 0 and delta.seconds <= 3600:
                # 刚刚（即一个小时内）
                update_date = constant.JD_TIME_FORMAT_JUST_NOW

            elif delta.days == 0:
                if delta.seconds < delta_to_today.seconds:
                    # 今天 12：00
                    update_date = constant.JD_TIME_FORMAT_TODAY.format(
                        update_time.hour, update_time.minute)
                else:
                    # 昨天 12：00
                    update_date = constant.JD_TIME_FORMAT_YESTERDAY.format(
                        update_time.hour, update_time.minute)

            elif delta.days == 1 and delta.seconds > delta_to_today.seconds:
                    #todo 考虑 跨月的情况， 不行的话可以考虑用 dateutil 包
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
