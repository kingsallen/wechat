# coding=utf-8

# @Time    : 1/22/17 16:12
# @Author  : towry (wanglintao@moseeker.com)
# @File    : __init__.py.py
# @DES     :

# Copyright 2016 MoSeeker

# -*- coding: utf-8 -*-

__all__ = ['Connector']


class Logger(object):
    def __init__(self):
        pass

    def debug(self):
        pass

    def info(self):
        pass

    def error(self):
        pass


class Connector(object):
    def __init__(self):
        self._logger = Logger()

    def set_logger(self, logger):
        self._logger = logger

    @property
    def logger(self):
        return self._logger
