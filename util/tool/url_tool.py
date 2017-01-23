# coding=utf-8

# @Time    : 9/18/16 17:22
# @Author  : panda (panyuxin@moseeker.com)
# @File    : url_tool.py
# @DES     : url 拼接

# Copyright 2016 MoSeeker

import urllib

from urllib.parse import urlparse, parse_qs, urlencode, parse_qsl, urlunparse
from setting import settings


def make_url(path, params=None, host="", protocol="https", escape=None,
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

    # 默认 query 黑名单：state, code, _xsrf , appid, tjtoken不传递
    _ESCAPE_DEFAULT = ['state', 'code', '_xsrf', 'appid', 'tjtoken']

    escape = set((escape or []) + _ESCAPE_DEFAULT)

    pairs = {k: v for k, v in params.items() if k not in escape}

    def valid(k, v):
        return v and isinstance(k, str) and isinstance(v, str) and not k.startswith("_")

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


def url_append_query(url, *args, **kwargs):
    """
        为url添加query
        :example: url_append_query('/m/app', "sjdf","lsdkjf", a=2)
    """
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))

    args_set = set(args)

    # 在args里删除那些即在args里面又在kwargs里的
    res = []
    if bool(kwargs):
        for key in args_set:
            if key not in kwargs:
                res.append(key)
        query.update(kwargs)
    else:
        res = args_set

    query_str = urlencode(query)
    # Add no value query.
    if len(res):
        count = 0
        for key in res:
            if count == 0 and not bool(query_str):
                query_str += "{}".format(key)
            else:
                query_str += "&{}".format(key)
            count += 1
    url_parts[4] = query_str

    return urlunparse(url_parts)


def make_static_url(path, protocol='https'):
    if not path:
        return None
    if not path.startswith("http"):
        path = urllib.parse.urljoin(settings['static_domain'], path)

    if not path.startswith("http") and protocol is not None:
        path = protocol + ":" + path
    return path
