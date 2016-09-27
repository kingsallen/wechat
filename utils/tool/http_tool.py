# coding=utf-8

# Copyright 2016 MoSeeker

"""
api 调用工具类，
调用时使用 infra=True/False 来基础服务的 api,还是其他的 api
"""
import requests
import tornado.httpclient
import ujson
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

from setting import settings


# def sync_http_get(route, jdata, timeout=5):
#
#     """尽量使用异步http请求,不得已才用
#     """
#
#     res = requests.get(route, params=jdata, timeout=timeout).json()
#     return res
#
# def sync_http_post(route, jdata, timeout=5):
#
#     """尽量使用异步http请求,不得已才用
#     """
#     res = requests.post(route, data=jdata, timeout=timeout).json()
#     return res

@gen.coroutine
def http_get(route, jdata, timeout=5, infra=False):
    ret = yield _async_http_get(route, jdata, timeout, infra, method='GET')
    raise gen.Return(ret)


@gen.coroutine
def http_delete(route, jdata, timeout=5, infra=False):
    ret = yield _async_http_get(route, jdata, timeout, infra, method='DELETE')
    raise gen.Return(ret)


@gen.coroutine
def http_post(route, jdata, timeout=5, infra=False):
    ret = yield _async_http_post(route, jdata, timeout, infra, method='POST')
    raise gen.Return(ret)


@gen.coroutine
def http_put(route, jdata, timeout=5, infra=False):
    ret = yield _async_http_post(route, jdata, timeout, infra, method='PUT')
    raise gen.Return(ret)


@gen.coroutine
def http_patch(route, jdata, timeout=5, infra=False):
    ret = yield _async_http_post(route, jdata, timeout, infra, method='PATCH')
    raise gen.Return(ret)


@gen.coroutine
def _async_http_get(route, jdata, api=None, timeout=5, infra=False, method='GET'):
    """
    如果数据正确，直接返回 data 数据，业务方不需要再解析 response 结构
    可用 HTTP 动词为 GET 和 DELETE
    """
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    url = url_concat("{0}/{1}".format(
        settings.infra if infra else api, route), jdata)
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
def _async_http_post(route, jdata, api=None, timeout=5, infra=False, method='POST'):
    """
    如果数据正确，直接返回data数据，业务方不需要再解析response结构
    可用 HTTP 动词为 POST, PATCH 和 PUT
    """
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    http_client = tornado.httpclient.AsyncHTTPClient()
    url = "{0}/{1}".format(settings.infra if infra else api, route)

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
