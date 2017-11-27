# coding=utf-8

# Copyright 2016 MoSeeker

"""基础服务 api 调用工具"""

import ujson
from urllib.parse import urlencode

import tornado.httpclient
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

import conf.common as constant
from globals import env, logger
from conf.common import INFRA_ERROR_CODES
from setting import settings
from util.common import ObjectDict
from util.common.exception import InfraOperationError
from util.tool.dict_tool import objectdictify


@gen.coroutine
def http_get(route, jdata=None, timeout=30, infra=True):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='GET',
                                infra=infra)
    return ret


@gen.coroutine
def http_delete(route, jdata=None, timeout=30, infra=True):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='DELETE',
                                infra=infra)
    return ret


@gen.coroutine
def http_post(route, jdata=None, timeout=30, infra=True):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='POST',
                                 infra=infra)
    return ret


@gen.coroutine
def http_put(route, jdata=None, timeout=30, infra=True):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PUT',
                                 infra=infra)
    return ret


@gen.coroutine
def http_patch(route, jdata=None, timeout=30, infra=True):
    ret = yield _async_http_post(route, jdata, timeout=timeout, method='PATCH',
                                 infra=infra)
    return ret


@gen.coroutine
def http_fetch(route, data=None, timeout=30):
    """使用 www-form 形式 HTTP 异步 POST 请求
    :param route:
    :param data:
    :param timeout:
    """

    if data is None:
        data = ObjectDict()

    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=1000)

    http_client = tornado.httpclient.AsyncHTTPClient()

    try:
        request = tornado.httpclient.HTTPRequest(
            route,
            method='POST',
            body=urlencode(data),
            request_timeout=timeout,
            headers=HTTPHeaders(
                {"Content-Type": "application/x-www-form-urlencoded"}
            ),
        )

        logger.info("[http_fetch][uri: {}][req_body: {}]".format(route, request.body))
        response = yield http_client.fetch(request)
        logger.info("[http_fetch][uri: {}][res_body: {}]".format(route, response.body))

    except tornado.httpclient.HTTPError as e:
        logger.warning("[http_fetch][uri: {}] httperror: {}".format(route, e))
        raise e
    else:
        return response.body


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

    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=1000)
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )

    logger.debug("[infra][http_{}][url: {}][ret: {}] ".format(
        method.lower(), url, ujson.decode(response.body)))

    body = objectdictify(ujson.decode(response.body))
    if infra and body.status in INFRA_ERROR_CODES:
        raise InfraOperationError(body.message)

    return body


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

    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=1000)
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
        .format(method.lower(), url, ujson.encode(jdata),
                ujson.decode(response.body)))

    body = objectdictify(ujson.decode(response.body))
    if infra and body.status in INFRA_ERROR_CODES:
        raise InfraOperationError(body.message)

    return body
