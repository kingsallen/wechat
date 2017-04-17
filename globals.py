# coding=utf-8

from tornado.options import options

from util.common.log import MessageLogger
from util.common.cache import BaseRedis
from util.common.es import BaseES

logger = MessageLogger(logpath=options.logpath)
redis = BaseRedis()
env = options.env
es = BaseES()
