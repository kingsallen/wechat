# coding=utf-8

# Copyright 2016 MoSeeker

"""基础服务 api 调用工具"""

import tornado.httpclient
import ujson
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

from app import env
from app import logger
from setting import settings
import conf.common as constant
from util.common import ObjectDict
from util.tool.dict_tool import objectdictify


@gen.coroutine
def http_get(route, jdata=None, timeout=5):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='GET')
    return ret


@gen.coroutine
def http_delete(route, jdata=None, timeout=5):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='DELETE')
    return ret


@gen.coroutine
def http_post(route, jdata=None, timeout=5):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='POST')
    return ret


@gen.coroutine
def http_put(route, jdata=None, timeout=5):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PUT')
    return ret


@gen.coroutine
def http_patch(route, jdata=None, timeout=5):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PATCH')
    return ret




def unboxing(http_response):
    """标准 restful api 返回拆箱"""

    result = bool(http_response.status == constant.API_SUCCESS)

    if result:
        data = http_response.data
    else:
        data = http_response

    return result, data


@gen.coroutine
def _async_http_get(route, jdata=None, timeout=5, method='GET'):
    """可用 HTTP 动词为 GET 和 DELETE"""
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    if jdata is None:
        jdata = ObjectDict()

    jdata.update({"appid": constant.APPID[env]})

    url = url_concat("{0}/{1}".format(settings['infra'], route), jdata)
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )

    logger.debug("[infra][_async_http_get][url: {}][ret: {}] ".format(
        url, ujson.decode(response.body)))
    body = ujson.decode(response.body)
    return objectdictify(body)


@gen.coroutine
def _async_http_post(route, jdata=None, timeout=5, method='POST'):
    """可用 HTTP 动词为 POST, PATCH 和 PUT"""
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    if jdata is None:
        jdata = ObjectDict()

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

    logger.debug(
        "[infra][_async_http_post][url: {}][body: {}][ret: {}] "
        .format(url, ujson.encode(jdata), ujson.decode(response.body)))
    body = ujson.decode(response.body)
    return objectdictify(body)
