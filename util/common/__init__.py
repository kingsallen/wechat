# coding=utf-8

import tornado.util


class ObjectDict(tornado.util.ObjectDict):
    """增强 ObjectDict 使其更易用

    增强
    1. 当访问的 key 不存在时返回 None
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None
