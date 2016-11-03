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
import conf.common as constant
from app import env
from app import logger


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

    # 指定 appid，必填
    jdata.update({"appid": constant.APPID[env]})

    url = url_concat("{0}/{1}".format(settings['infra'], route), jdata)
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url, request_timeout=timeout, method=method.upper(),
        headers=HTTPHeaders({"Content-Type": "application/json"}))

    logger.debug("[infra][_async_http_get][url: {}][ret: {}] ".format(url, ujson.decode(response.body)))
    raise gen.Return(ObjectDict(ujson.decode(response.body)))


@gen.coroutine
def _async_http_post(route, jdata, timeout=5, method='POST'):
    """可用 HTTP 动词为 POST, PATCH 和 PUT"""
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    # 指定 appid，必填
    jdata.update({"appid": constant.APPID[env]})

    http_client = tornado.httpclient.AsyncHTTPClient()
    url = "{0}/{1}".format(settings['infra'], route)
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        body=ujson.encode(jdata),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )
    logger.debug("[infra][_async_http_post][url: {}][body: {}][ret: {}] ".format(url, ujson.encode(jdata), ujson.decode(response.body)))
    raise gen.Return(ObjectDict(ujson.decode(response.body)))


@gen.coroutine
def async_das_get(route, jdata, timeout=5, method='GET'):
    """可用 HTTP 动词为 GET 和 DELETE
    临时接 DAS 使用，后续迁移到基础服务"""

    logger.debug("[infra][async_das_get][jdata: {}] ".format(jdata))
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    url = url_concat("{0}/{1}".format(settings['das'], route), jdata)
    logger.debug("[infra][async_das_get][url: {}] ".format(url))
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url, request_timeout=timeout, method=method.upper())

    logger.debug("[infra][async_das_get][url: {}][ret: {}] ".format(url, ujson.decode(response.body)))
    raise gen.Return(ObjectDict(ujson.decode(response.body)))


@gen.coroutine
def async_das_post(route, jdata, timeout=5):
    """临时接 DAS 使用，后续迁移到基础服务"""

    http_client = tornado.httpclient.AsyncHTTPClient()
    url = "{0}/{1}".format(settings['das'], route),
    response = yield http_client.fetch(
        url,
        method="POST",
        body=ujson.encode(jdata),
        request_timeout=timeout,
    )

    logger.debug("[infra][_async_http_post][url: {}][body: {}][ret: {}] ".format(url, ujson.encode(jdata), ujson.decode(response.body)))
    raise gen.Return(ObjectDict(ujson.decode(response.body)))
