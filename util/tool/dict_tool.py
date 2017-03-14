# coding=utf-8

from util.common import ObjectDict


def sub_dict(somedict, somekeys, default=None):
    if isinstance(somekeys, list):
        ret = {k: somedict.get(k, default) for k in somekeys}
    elif isinstance(somekeys, str):
        key = somekeys
        ret = {key: somedict.get(key, default)}
    else:
        raise ValueError('sub dict key should be list or str')
    return ObjectDict(ret)


def objectdictify(result):
    """将结果 ObjectDict 化"""
    ret = result

    if isinstance(result, list):
        ret = []
        for e in result:
            if isinstance(e, dict):
                ret.append(ObjectDict(e))
            else:
                ret.append(e)
    elif isinstance(result, dict):
        ret = ObjectDict(result)

    else: pass

    return ret

