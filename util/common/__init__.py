# coding=utf-8

import tornado.util


class ObjectDict(tornado.util.ObjectDict):
    """增强 ObjectDict 使其更易用

    增强
    1. 当访问的 key 不存在时返回 None

    例
    判断一个 key 是否存在，
    以前需要   `'key' in object_dict and object_dict.key`
    现在只需要 `object_dict.key`

    2. 初始化时将内嵌的所有 dict 都改成 ObjectDict
    例
    d = {'a': 1, 'b': {'c': 2}}
    dd = ObjectDict(d)
    print(dd.b.c)  => 2
    """

    def __init__(self, *args, **kwargs):
        super(ObjectDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for t in arg.items():
                    self[t[0]] = (
                        self.__class__(t[1]) if isinstance(t[1], dict) else t[1])
        if kwargs:
            for t in kwargs.items():
                self[t[0]] = self.__class__(t[1]) if isinstance(t[1], dict) else t[1]

    def __getattr__(self, key):
        try:
            return super().__getattr__(key)
        except AttributeError:
            return None
