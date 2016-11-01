# coding=utf-8

# Copyright 2016 MoSeeker

"""
时间工具类
"""

from datetime import datetime

import conf.common as constant
from app import logger


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
    logger.debug("update_date 1: %s" % update_date)
    logger.debug("update_time: %s" % type(update_time))
    try:
        if update_time:
            pass_day = datetime.now() - update_time

            logger.debug("pass_day 1: %s" % pass_day.seconds)
            logger.debug("pass_day 2: %s" % pass_day.days)

            if pass_day.days == 0 and pass_day.seconds <= 3600:
                # 刚刚（即一个小时内）
                logger.debug("update_date 2: %s" % update_date)
                update_date = constant.JD_TIME_FORMAT_JUST_NOW

            elif pass_day.days == 0:
                # 今天 12：00
                logger.debug("update_date 3: %s" % update_date)
                update_date = constant.JD_TIME_FORMAT_TODAY.format(
                    update_time.hour, update_time.minute)


            elif pass_day.days == 1:
                # 昨天 12：00
                logger.debug("update_date 4: %s" % update_date)
                update_date = constant.JD_TIME_FORMAT_YESTERDAY.format(
                    update_time.hour, update_time.minute)

            else:
                # 2016-11-23
                logger.debug("update_date 5: %s" % update_date)
                update_date = constant.JD_TIME_FORMAT_FULL.format(
                    update_time.year, update_time.month, update_time.day)

    except Exception as e:
        logger.error(e)
        pass
    finally:
        return update_date
