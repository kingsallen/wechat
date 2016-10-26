# coding=utf-8

# Copyright 2016 MoSeeker

"""
基础服务 api 调用工具类，
"""

import tornado.httpclient
import ujson
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

from util.common import ObjectDict
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
    """可用 HTTP 动词为 GET 和 DELETE"""
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    url = url_concat("{0}/{1}".format(settings['infra'], route), jdata)
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url, request_timeout=timeout, method=method.upper(),
        headers=HTTPHeaders({"Content-Type": "application/json"}))

    raise gen.Return(ObjectDict(ujson.decode(response.body)))


@gen.coroutine
def _async_http_post(route, jdata, timeout=5, method='POST'):
    """可用 HTTP 动词为 POST, PATCH 和 PUT"""
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    http_client = tornado.httpclient.AsyncHTTPClient()
    url = "{0}/{1}".format(settings['infra'], route)
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        body=ujson.encode(jdata),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )
    raise gen.Return(ObjectDict(ujson.decode(response.body)))
