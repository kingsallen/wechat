# coding=utf-8

# @Time    : 9/18/16 17:22
# @Author  : panda (panyuxin@moseeker.com)
# @File    : url_tool.py
# @DES     : url 拼接

# Copyright 2016 MoSeeker

import urllib


def make_url(path, params=None, host="", protocol="http", escape=None,
             **kwargs):

    if "?" in path:
        raise ValueError("Path should not contain '?'")

    if not params:
        params = {}
    if not isinstance(params, dict):
        raise TypeError("Params is not a dict")

    if not isinstance(escape, list):
        escape = []

    d = params.copy()
    # m 参数不传递
    d.pop('m', None)

    d.update(kwargs)

    url_params = []
    for k, v in d.items():
        if k in escape:
            continue

        if not (isinstance(k, basestring) and isinstance(v, basestring)):
            continue

        if v == '':
            continue

        if k.startswith("_") and k not in kwargs:
            continue

        k = urllib.quote(str(k))
        if k in ["wechat_signature"]:
            kv = k + "=" + str(v)
        else:
            kv = k + "=" + urllib.quote(str(v) if str(v) else "")

        url_params.append(kv)

    return (((protocol + "://" + host) if host else "") +
            path + "?" + ("&".join(url_params)))
