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
def http_get(route, jdata=None, timeout=5, infra=True):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='GET', infra=infra)
    return ret

@gen.coroutine
def http_delete(route, jdata=None, timeout=5, infra=True):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='DELETE', infra=infra)
    return ret

@gen.coroutine
def http_post(route, jdata=None, timeout=5, infra=True):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='POST', infra=infra)
    return ret

@gen.coroutine
def http_put(route, jdata=None, timeout=5, infra=True):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PUT', infra=infra)
    return ret

@gen.coroutine
def http_patch(route, jdata=None, timeout=5, infra=True):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PATCH', infra=infra)
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
def _async_http_get(route, jdata=None, timeout=5, method='GET', infra=True):
    """可用 HTTP 动词为 GET 和 DELETE"""
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    if jdata is None:
        jdata = ObjectDict()

    if infra:
        jdata.update({"appid": constant.APPID[env]})
        url = url_concat("{0}/{1}".format(settings['infra'], route), jdata)
    else:
        url = url_concat(route, jdata)

    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )

    logger.debug("[infra][http_{}][url: {}][ret: {}] ".format(
        method.lower(), url, ujson.decode(response.body)))
    body = ujson.decode(response.body)
    return objectdictify(body)


@gen.coroutine
def _async_http_post(route, jdata=None, timeout=5, method='POST', infra=True):
    """可用 HTTP 动词为 POST, PATCH 和 PUT"""
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    if jdata is None:
        jdata = ObjectDict()

    if infra:
        jdata.update({"appid": constant.APPID[env]})
        url = "{0}/{1}".format(settings['infra'], route)
    else:
        url = route

    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        body=ujson.encode(jdata),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )

    logger.debug(
        "[infra][http_{}][url: {}][body: {}][ret: {}] "
        .format(method.lower(), url, ujson.encode(jdata), ujson.decode(response.body)))
    body = ujson.decode(response.body)
    return objectdictify(body)
