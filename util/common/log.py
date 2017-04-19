# coding=utf-8

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from tornado.log import gen_log

from util.common.elk import RedisELK

# --------------------------------------------------------------------------
#  Configurations
# --------------------------------------------------------------------------

LOGGER_NAME = 'DQLogger'

FORMATER = logging.Formatter(
    u'%(asctime)s\t%(pathname)s:%(lineno)s\t%(levelname)s\t%(message)s')

SUFFIX = '%Y%m%d%H.log'

# Highest built-in level is 50, so make STATS as 60
logging.addLevelName(60, 'STATS')

LOG_LEVELS = {
    'DEBUG':    logging.DEBUG,
    'INFO':     logging.INFO,
    'WARN':     logging.WARN,
    'ERROR':    logging.ERROR,
    'STATS':    logging.getLevelName('STATS')
}

# --------------------------------------------------------------------------
#  Logger class and functions
# --------------------------------------------------------------------------


class ExactLogLevelFilter(logging.Filter):
    """The filter appended to handlers"""
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno == self.__level


class Logger(object):
    """3rd-party package independent logger root class"""

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
            'STATS':    os.path.join(logpath, 'stats/stats.log'),
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
            self._handlers[level].setLevel(LOG_LEVELS[level])
            self._handlers[level].addFilter(
                ExactLogLevelFilter(LOG_LEVELS[level]))

            self.__logger.addHandler(self._handlers[level])
            self.__tornado_gen_log.addHandler(self._handlers[level])

    def debug(self, message):
        self.__logger.debug(message, exc_info=0)

    def info(self, message):
        self.__logger.info(message, exc_info=0)

    def warning(self, message):
        self.__logger.warning(message, exc_info=0)

    def warn(self, message):
        self.warning(message)

    def error(self, message):
        self.__logger.error(message, exc_info=0)

    def stats(self, message):
        self.__logger.log(
            logging.getLevelName("STATS"), message, exc_info=0)


class MessageLogger(Logger):
    """MessageLogger can push the message to redis"""

    def __init__(self, **kwargs):
        super(MessageLogger, self).__init__(**kwargs)
        self.impl = RedisELK()

    def debug(self, message):
        super(MessageLogger, self).debug(message)

    def info(self, message):
        super(MessageLogger, self).info(message)

    def warning(self, message):
        super(MessageLogger, self).warning(message)

    def warn(self, message):
        self.warning(message)

    def error(self, message):
        super(MessageLogger, self).error(message)
        # error 及时报警
        # Alarm.biu(message)
        # Alarm.biu(traceback.format_exc())

    def stats(self, message):
        super(MessageLogger, self).stats(message)
        self.impl.send_message("stats", message)
