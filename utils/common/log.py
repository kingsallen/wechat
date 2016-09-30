# coding=utf-8

# Copyright 2016 MoSeeker

"""
logger 类: 按级别分文件打印日志,
不依赖第三方库
"""
import redis
import logging
import os
from setting import settings
from logging.handlers import TimedRotatingFileHandler
from cache import BaseCache


# --------------------------------------------------------------------------
#  Configurations
# --------------------------------------------------------------------------

LOGGER_NAME = 'DQLogger'
FORMATER = logging.Formatter(
    u'%(asctime)s\t%(pathname)s:%(lineno)s\t%(levelname)s\t%(message)s'
)
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

class RedisLog(BaseCache):

    def __init__(self, redis):
        super(RedisLog, self).__init__(redis)

pool = redis.ConnectionPool(host=settings["elk"]["redis_host"],
                            port=settings["elk"]["redis_port"])

redis = redis.StrictRedis(connection_pool=pool)

class Logger(object):

    def __init__(self, logpath='/tmp/', log_backcount=0,
                 log_filesize=10 * 1024 * 1024):
        self.__logger = logging.getLogger(LOGGER_NAME)
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
        self.redis_log = RedisLog(redis=redis)

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

    def debug(self, message):
        self.__logger.debug(message, exc_info=0)
        self.redis_log.lpush("debug", message)

    def info(self, message):
        self.__logger.info(message, exc_info=0)
        self.redis_log.lpush("info", message)

    def warn(self, message):
        self.__logger.warn(message, exc_info=0)
        self.redis_log.lpush("warn", message)

    def error(self, message):
        self.__logger.error(message, exc_info=0)
        self.redis_log.lpush("error", message)

    def record(self, message):
        self.__logger.log(
            logging.getLevelName("CUSTOMER"), message, exc_info=0)
        self.redis_log.lpush("record", message)
        self.redis_log.set("hello", {"a": 12345})
