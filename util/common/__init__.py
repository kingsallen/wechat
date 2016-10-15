# coding=utf-8

import tornado.util


class ObjectDict(tornado.util.ObjectDict):
    """增强 ObjectDict 使其更易用

    增强
    1. 当访问的 key 不存在时返回 None
    比如获取一个值，
    以前需要   `'key' in object_dict and object_dict.key`
    现在只需要 `object_dict.key`
    """
    def __getattr__(self, key):
        try:
            return super().__getattr__(key)
        except AttributeError:
            return None
