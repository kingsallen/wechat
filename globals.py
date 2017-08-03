# coding=utf-8

from tornado.options import options

import util.common.mq as mq
from util.common.log import MessageLogger
from util.common.cache import BaseRedis
from util.common.es import BaseES

options.parse_command_line()
logger = MessageLogger(logpath=options.logpath)
redis = BaseRedis()
env = options.env
es = BaseES()

award_publisher = mq.award_publisher

