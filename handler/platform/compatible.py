# coding=utf-8

# @Time    : 5/5/17 11:02
# @Author  : panda (panyuxin@moseeker.com)
# @File    : compatible.py
# @DES     :

from tornado import gen

from handler.base import BaseHandler


class CompatibleHandler(BaseHandler):

    def get(self):
        self.write_error(404)
