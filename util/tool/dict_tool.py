# coding=utf-8


def sub_dict(somedict, somekeys, default=None):
    return {k: somedict.get(k, default) for k in somekeys}
