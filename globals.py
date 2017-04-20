# coding=utf-8

from tornado.options import options
from util.common.log import MessageLogger
from util.common.cache import BaseRedis

logger = MessageLogger(logpath=options.logpath)
redis = BaseRedis()
env = options.env
