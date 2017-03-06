# coding=utf-8

# @Time    : 3/6/17 10:55
# @Author  : panda (panyuxin@moseeker.com)
# @File    : application.py
# @DES     :

from tornado import gen

import conf.common as const
import conf.message as msg

from handler.base import BaseHandler
from util.common.decorator import handle_response

class ApplicationHandler(BaseHandler):

    def get(self):
        pass
