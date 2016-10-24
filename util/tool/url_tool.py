# coding=utf-8

# @Time    : 9/18/16 17:22
# @Author  : panda (panyuxin@moseeker.com)
# @File    : url_tool.py
# @DES     : url 拼接

# Copyright 2016 MoSeeker

from urllib.parse import urlparse, parse_qs, urlencode, quote


def make_url(path, params=None, host="", protocol="http", escape=None,
             **kwargs):

    # TODO
    # 需要过滤 xsrf
    # 对于 v 为中文的，是否需要进行 urlencode

    if "?" in path:
        raise ValueError("Path should not contain '?'")

    if not isinstance(params, dict):
        raise TypeError("Params is not a dict")

    params = params or {}

    escape_default = ['m', 'state', 'code']
    escape = escape or []
    escape = set(escape_default + escape)

    d = params.copy()

    for e in escape:
        d.pop(e, None)
    d.update(kwargs)

    url_params = []
    for k, v in d.items():
        if k in escape:
            continue

        if not (isinstance(k, str) and isinstance(v, str)):
            continue

        if v == '':
            continue

        if k.startswith("_") and k not in kwargs:
            continue

        k = quote(str(k))
        if k in ["wechat_signature"]:
            kv = k + "=" + str(v)
        else:
            kv = k + "=" + quote(str(v) if str(v) else "")

        url_params.append(kv)

    return (((protocol + "://" + host) if host else "") +
            path + "?" + ("&".join(url_params)))


def url_subtract_query(url, query_key_list):
    """削减 url 的 query 中指定的键值"""
    p = urlparse(url)
    qurey = p.query
    parsed_query = parse_qs(qurey)
    for l in query_key_list:
        parsed_query.pop(l, None)
    nquery = urlencode(parsed_query, doseq=True)
    return "{scheme}://{netloc}{path}?{query}".format(
        scheme=p[0], netloc=p[1], path=p[2], query=nquery)


