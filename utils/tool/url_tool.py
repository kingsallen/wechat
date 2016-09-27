# coding=utf-8

# @Time    : 9/18/16 17:22
# @Author  : panda (panyuxin@moseeker.com)
# @File    : url_tool.py
# @DES     : url 拼接

# Copyright 2016 MoSeeker

import urllib
from utils.tool.date_tool import curr_now_pure

def make_url(path, params, host="", protocol="http", encode_url=True,
             escape=None, **kwargs):

    if "?" in path:
        raise ValueError("Path should not contain '?'")

    if not isinstance(params, dict):
        raise TypeError("Params is not a dict")

    if not isinstance(escape, list):
        escape = []

    # TODO 是否可以去除
    # escape_excluded = ["pid", "next_url", "wechat_signature", "url", "headimg"]
    # escape = list(set(escape) - set(escape_excluded))

    d = params.copy()

    # 增加tjtoken，作为统计，串联用户访问链路
    if not d.get("tjtoken", None):
        d['tjtoken'] = curr_now_pure()

    # m 和 _method 参数不传递
    d.pop('m', None)
    d.pop('_method', None)

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

        k = urllib.quote(k)
        if k not in ["wechat_signature", "next_url"]:
            kv = k + "=" + urllib.quote(str(v) if str(v) else "")
        else:
            kv = k + "=" + str(v)
        url_params.append(kv)

    return (((protocol + "://" + host) if host else "") +
            path + "?" + ("&".join(url_params)))

if __name__ == '__main__':
    print make_url("/mobile/position",
                   dict(aa='897',abc='group departmen&t',
                        wechat_signature="aaa=="),
                   host='localhost',
                   encode_url=True,
                   escape=['aa'])
    print urllib.unquote("%E8%BF%99%E6%98%AF")
