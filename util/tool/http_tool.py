# coding=utf-8

# Copyright 2016 MoSeeker

"""
基础服务 api 调用工具类，
"""

import tornado.httpclient
import ujson
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

from setting import settings


@gen.coroutine
def http_get(route, jdata, timeout=5):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='GET')
    raise gen.Return(ret)


@gen.coroutine
def http_delete(route, jdata, timeout=5):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='DELETE')
    raise gen.Return(ret)


@gen.coroutine
def http_post(route, jdata, timeout=5):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='POST')
    raise gen.Return(ret)


@gen.coroutine
def http_put(route, jdata, timeout=5):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PUT')
    raise gen.Return(ret)


@gen.coroutine
def http_patch(route, jdata, timeout=5):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PATCH')
    raise gen.Return(ret)


@gen.coroutine
def _async_http_get(route, jdata, timeout=5, method='GET'):
    """如果数据正确，直接返回 data 数据，业务方不需要再解析 response 结构
    可用 HTTP 动词为 GET 和 DELETE
    """
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    url = url_concat("{0}/{1}".format(settings.infra, route), jdata)
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url, request_timeout=timeout, method=method.upper(),
        headers=HTTPHeaders({"Content-Type": "application/json"}))
    body = ujson.decode(response.body)
    content_type = response.headers.get('Content-Type', '')
    if body.get('status') == 0 and "application/json" in content_type:
        raise gen.Return(body.get('data'))
    raise gen.Return(body)


@gen.coroutine
def _async_http_post(route, jdata, timeout=5, method='POST'):
    """如果数据正确，直接返回data数据，业务方不需要再解析response结构
    可用 HTTP 动词为 POST, PATCH 和 PUT
    """
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    http_client = tornado.httpclient.AsyncHTTPClient()
    url = "{0}/{1}".format(settings.infra, route)
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        body=ujson.encode(jdata),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )
    body = ujson.decode(response.body)
    content_type = response.headers.get('Content-Type', '')
    if body.get('status', 0) == 0 and "application/json" in content_type:
        raise gen.Return(body.get('data'))
    raise gen.Return(body)
