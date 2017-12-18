# coding=utf-8

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from tornado.log import gen_log

from util.common.elk import RedisELK
from util.common.singleton import Singleton

# --------------------------------------------------------------------------
#  Configurations
# --------------------------------------------------------------------------

LOGGER_NAME = 'DQLogger'

FORMATER = logging.Formatter(
    u'%(asctime)s\t%(pathname)s:%(lineno)s\t%(levelname)s\t%(message)s')

SUFFIX = '%Y%m%d%H.log'

# Highest built-in level is 50, so make STATS as 60
STATS_LEVEL = 60
logging.addLevelName(STATS_LEVEL, 'STATS')

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARN': logging.WARN,
    'ERROR': logging.ERROR,
    'STATS': STATS_LEVEL
}


# --------------------------------------------------------------------------
#  Logger class and functions
# --------------------------------------------------------------------------

class LeveledTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__log_level = level

    def emit(self, record):
        if record.levelno == self.__log_level:
            super().emit(record)
        else:
            pass


class Logger(object, metaclass=Singleton):
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
            'DEBUG': os.path.join(logpath, 'debug/debug.log'),
            'INFO': os.path.join(logpath, 'info/info.log'),
            'WARN': os.path.join(logpath, 'warn/warn.log'),
            'ERROR': os.path.join(logpath, 'error/error.log'),
            'STATS': os.path.join(logpath, 'stats/stats.log'),
        }
        self._create_handlers()

    def _create_handlers(self):
        log_levels = self.log_path.keys()

        for level_name in log_levels:
            handler = self.__create_file_handler(level_name)
            self._handlers[level_name] = handler
            self.__logger.addHandler(handler)
            self.__tornado_gen_log.addHandler(handler)

    def __create_file_handler(self, level_name):
        level_value = LOG_LEVELS[level_name]
        path = os.path.abspath(self.log_path[level_name])

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        handler = LeveledTimedRotatingFileHandler(
            level_value, path, backupCount=self._log_backcount)
        handler.setFormatter(FORMATER)
        handler.suffix = SUFFIX
        handler.setLevel(level_value)

        return handler

    def debug(self, message):
        self.__logger.debug(message, exc_info=0)

    def info(self, message):
        self.__logger.info(message, exc_info=0)

    def warning(self, message):
        self.__logger.warning(message, exc_info=0)

    def warn(self, message):
        self.warning(message)

    def error(self, message):
        self.__logger.error(message, exc_info=1)

    def stats(self, message):
        self.__logger.log(logging.getLevelName("STATS"), message, exc_info=0)


class MessageLogger(Logger):
    """MessageLogger can push the message to redis"""

    def __init__(self, **kwargs):
        super(MessageLogger, self).__init__(**kwargs)
        self.impl = RedisELK()

    def debug(self, message):
        super(MessageLogger, self).debug(message)

    def info(self, message):
        super(MessageLogger, self).info(message)
        self.impl.send_message("info", message)

    def warning(self, message):
        super(MessageLogger, self).warning(message)
        self.impl.send_message("warn", message)

    def warn(self, message):
        self.warning(message)

    def error(self, message):
        super(MessageLogger, self).error(message)
        self.impl.send_message("error", message)

    def stats(self, message):
        super(MessageLogger, self).stats(message)
        self.impl.send_message("stats", message)
