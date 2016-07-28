# coding: utf-8

'''
时间工具类
'''

from datetime import datetime

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
            zero = datetime(
                update_time.year, update_time.month, update_time.day, 0, 0, 0)

            pass_day = datetime.now() - zero

            if datetime.now().year != update_time.year:
                update_date = constant.JD_TIME_FORMAT_FULL.format(
                    update_time.year, update_time.month, update_time.day)

            elif pass_day.days <= 0 and pass_day.seconds <= 3600:
                # 刚刚（即一个小时内）
                update_date = constant.JD_TIME_FORMAT_JUST_NOW

            elif pass_day.days <= 0:
                # 今天 12：00
                update_date = constant.JD_TIME_FORMAT_TODAY.format(
                    update_time.hour, update_time.minute)

            elif pass_day.days == 1:
                # 昨天 12：00
                update_date = constant.JD_TIME_FORMAT_YESTERDAY.format(
                    update_time.hour, update_time.minute)
            else:
                # 11-23
                update_date = constant.JD_TIME_FORMAT_THIS_YEAR.format(
                    update_time.month, update_time.day)
    except Exception:
        pass
    finally:
        return update_date
