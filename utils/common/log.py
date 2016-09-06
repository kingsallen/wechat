# coding=utf-8

# Copyright 2016 MoSeeker

"""
DQLogger

merge tornado gen_log
do not merge tornado app_log & access_log
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from tornado.log import gen_log
from utils.common.alarm import Alarm

# --------------------------------------------------------------------------
#  Configurations
# --------------------------------------------------------------------------

LOGGER_NAME = 'DQLogger'

FORMATER = logging.Formatter(
    u'%(asctime)s\t%(pathname)s:%(lineno)s\t%(levelname)s\t%(message)s')

SUFFIX = '%Y%m%d%H.log'

# Highest built-in level is 50, so make CUSTOMER as 60
logging.addLevelName(60, 'CUSTOMER')

LOG_LEVELS = {
    'DEBUG':    logging.DEBUG,
    'INFO':     logging.INFO,
    'WARN':     logging.WARN,
    'ERROR':    logging.ERROR,
    'CUSTOMER': logging.getLevelName('CUSTOMER')
}

# --------------------------------------------------------------------------
#  Logger class and functions
# --------------------------------------------------------------------------


class ExactLogLevelFilter(logging.Filter):
    """
    The filter appended to handlers
    """
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno == self.__level


class Logger(object):

    def __init__(self, logpath='/tmp/', log_backcount=0,
                 log_filesize=10 * 1024 * 1024):
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__tornado_gen_log = gen_log
        self.__logger.setLevel(logging.DEBUG)  # set debug as base level

        self._handlers = dict()
        self._log_backcount = log_backcount
        self._log_filesize = log_filesize

        self.log_path = {
            'DEBUG':    os.path.join(logpath, 'debug/debug.log'),
            'INFO':     os.path.join(logpath, 'info/info.log'),
            'WARN':     os.path.join(logpath, 'warn/warn.log'),
            'ERROR':    os.path.join(logpath, 'error/error.log'),
            'CUSTOMER': os.path.join(logpath, 'customer/customer.log'),
        }

        self._create_handlers()

    def _create_handlers(self):
        log_levels = self.log_path.keys()

        for level in log_levels:
            path = os.path.abspath(self.log_path[level])

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            self._handlers[level] = TimedRotatingFileHandler(
                path, backupCount=self._log_backcount)
            self._handlers[level].setFormatter(FORMATER)
            self._handlers[level].suffix = SUFFIX
            self._handlers[level].addFilter(
                ExactLogLevelFilter(LOG_LEVELS[level]))

            self.__logger.addHandler(self._handlers[level])
            self.__tornado_gen_log.addHandler(self._handlers[level])

    def debug(self, message):
        self.__logger.debug(message, exc_info=0)

    def info(self, message):
        self.__logger.info(message, exc_info=0)

    def warn(self, message):
        self.__logger.warn(message, exc_info=0)

    def error(self, message):
        self.__logger.error(message, exc_info=1)
        Alarm.biu(message)

    def record(self, message):
        self.__logger.log(
            logging.getLevelName("CUSTOMER"), message, exc_info=0)
