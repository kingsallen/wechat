# coding=utf-8

# @Time    : 9/18/16 17:22
# @Author  : panda (panyuxin@moseeker.com)
# @File    : url_tool.py
# @DES     : url 拼接

# Copyright 2016 MoSeeker

from urllib.parse import urlparse, parse_qs, urlencode


def make_url(path, params=None, host="", protocol="http", escape=None,
             **kwargs):
    """
    生成 url 的 helper 方法， 一般在 handler 调用
    :param path: url path
    :param params: url query
    :param host: hostname
    :param protocol: http/https
    :param escape: url query 黑名单
    :param kwargs: 额外手动添加的 url query
    :return: string of url
    """

    params = params or {}

    if "?" in path:
        raise ValueError("Path should not contain '?'")

    if not isinstance(params, dict):
        raise TypeError("Params is not a dict")

    params.update(kwargs)

    # 默认 query 黑名单：m, state, code, _xsrf , appid不传递
    _ESCAPE_DEFAULT = ['m', 'state', 'code', '_xsrf', 'appid']

    escape = set((escape or []) + _ESCAPE_DEFAULT)

    pairs = {k: v for k, v in params.items() if k not in escape}

    def valid(k, v):
        return v and isinstance(k, str) and isinstance(v, str)

    query = [(k, v) for k, v in pairs.items() if valid(k, v)]

    ret = (((protocol + "://" + host) if host else "") + path + "?" +
           urlencode(query))

    return ret[:-1] if ret[-1] == '?' else ret


def url_subtract_query(url, exclude):
    """削减 url 的 query 中指定的键值"""
    p = urlparse(url)
    query = p.query
    parsed_query = {k: v for k, v in parse_qs(query).items()
                    if k not in exclude}

    ret = "{scheme}://{netloc}{path}?{query}".format(
        scheme=p[0], netloc=p[1], path=p[2],
        query=urlencode(parsed_query, doseq=True))

    return ret[:-1] if ret[-1] == '?' else ret
