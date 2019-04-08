# coding=utf-8

# Copyright 2016 MoSeeker

"""基础服务 api 调用工具"""
import ast
import ujson
import tornado.httpclient

from urllib.parse import urlencode
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

import conf.common as constant

from conf.common import INFRA_ERROR_CODES
from globals import env, logger
from setting import settings
from util.common import ObjectDict
from util.common.exception import InfraOperationError
from util.tool.dict_tool import objectdictify
from util.tool.str_tool import json_underline2hump, json_hump2underline, params_underline2hump


@gen.coroutine
def http_get_v2(route, service, jdata=None, timeout=30):
    route = "{0}/{1}{2}".format(settings['cloud'], service.service_name, route)
    jdata = _serialize_data(service, jdata)
    ret = yield _v2_async_http_get(route, jdata, timeout=timeout, method='GET')
    return ret


@gen.coroutine
def http_post_v2(route, service, jdata=None, timeout=30):
    route = _serialize_uri(service, route)
    ret = yield _v2_async_http_post(route, jdata, timeout=timeout, method='POST')
    return ret


@gen.coroutine
def http_delete_v2(route, service, jdata=None, timeout=30):
    route = "{0}/{1}{2}".format(settings['cloud'], service.service_name, route)
    jdata = _serialize_data(service, jdata)
    ret = yield _v2_async_http_get(route, jdata, timeout=timeout, method='DELETE')
    return ret


@gen.coroutine
def http_put_v2(route, service, jdata=None, timeout=30):
    route = _serialize_uri(service, route)
    ret = yield _v2_async_http_post(route, jdata, timeout=timeout, method='PUT')
    return ret


@gen.coroutine
def http_patch_v2(route, service, jdata=None, timeout=30):
    route = _serialize_uri(service, route)
    ret = yield _v2_async_http_post(route, jdata, timeout=timeout, method='PATCH')
    return ret


def _serialize_uri(service, route):
    return "{0}/{1}{2}?appid={appid}&interfaceid={interfaceid}".format(
        settings['cloud'],
        service.service_name,
        route,
        appid=service.appid,
        interfaceid=service.interfaceid
    )


def _serialize_data(service, jdata):
    if isinstance(jdata, list):
        jdata.append(("appid", service.appid))
        jdata.append(("interfaceid", service.interfaceid))
    elif isinstance(jdata, dict):
        jdata.update({"appid": service.appid, "interfaceid": service.interfaceid})
    else:
        jdata = {"appid": service.appid, "interfaceid": service.interfaceid}
    return jdata


@gen.coroutine
def http_get(route, jdata=None, timeout=30, infra=True, headers=None):
    ret = yield _async_http_get(route, jdata, timeout=timeout, method='GET',
                                infra=infra, headers=headers)
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


tornado.httpclient.AsyncHTTPClient.configure(
    "tornado.simple_httpclient.SimpleAsyncHTTPClient", max_clients=settings["async_http_client_max_clients"])


@gen.coroutine
def http_fetch(route, data=None, timeout=30, raise_error=True):
    """使用 www-form 形式 HTTP 异步 POST 请求
    :param route:
    :param data:
    :param timeout:
    :param raise_error:
    """

    if data is None:
        data = ObjectDict()

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
        response = yield http_client.fetch(request, raise_error=raise_error)
        logger.info("[http_fetch][uri: {}][res_body: {}]".format(route, response.body))

    except tornado.httpclient.HTTPError as e:
        logger.warning("[http_fetch][uri: {}] httperror: {}".format(route, e))
        raise e
    else:
        return response.body


@gen.coroutine
def http_post_cs_msg(route, data=None, timeout=30, raise_error=True):
    """使用 www-form 形式 HTTP 异步 POST 请求
    :param route:
    :param data:
    :param timeout:
    :param raise_error:
    """

    if data is None:
        data = ObjectDict()

    http_client = tornado.httpclient.AsyncHTTPClient()

    try:
        request = tornado.httpclient.HTTPRequest(
            route,
            method='POST',
            body=ujson.dumps(data, ensure_ascii=False),
            request_timeout=timeout,
            headers=HTTPHeaders(
                {"Content-Type": "application/x-www-form-urlencoded"}
            ),
        )

        logger.info("[http_fetch][uri: {}][req_body: {}]".format(route, request.body))
        response = yield http_client.fetch(request, raise_error=raise_error)
        logger.info("[http_fetch][uri: {}][res_body: {}]".format(route, response.body))

    except tornado.httpclient.HTTPError as e:
        logger.warning("[http_fetch][uri: {}] httperror: {}".format(route, e))
        raise e
    else:
        return response.body


@gen.coroutine
def http_post_multipart_form(route, form, timeout=30, raise_error=True, headers=None):
    """使用multipart/form-data形式 HTTP 异步 POST 请求
    :param route:
    :param form:
    :param timeout:
    :param raise_error:
    """
    if form is None:
        form = ObjectDict()

    http_client = tornado.httpclient.AsyncHTTPClient()

    try:
        request = tornado.httpclient.HTTPRequest(
            route,
            method='POST',
            body=form,
            request_timeout=timeout,
            headers=headers,
        )

        logger.info("[http_post_multipart_form][uri: {}]".format(route))
        response = yield http_client.fetch(request, raise_error=raise_error)
        logger.info("[http_post_multipart_form][uri: {}][res_body: {}]".format(route, response.body))

    except tornado.httpclient.HTTPError as e:
        logger.warning("[http_post_multipart_form][uri: {}] httperror: {}".format(route, e))
        raise e
    else:
        body = objectdictify(ujson.decode(response.body))
        if body.status in INFRA_ERROR_CODES:
            raise InfraOperationError(body.message)

        return body


def unboxing(http_response):
    """标准 restful api 返回拆箱"""

    result = bool(http_response.status == constant.API_SUCCESS)

    if result:
        data = http_response.data
    else:
        data = http_response
    return result, data


def unboxing_fetchone(http_response):
    """解析服务返回结果，返回结果非对象，而是列表且列表数据为对象时，取列表第一条记录"""

    result = bool(http_response.code == constant.NEWINFRA_API_SUCCESS)
    data = ObjectDict()
    if result:
        if isinstance(http_response.data, list):
            if http_response.data and isinstance(http_response.data[0], dict):
                data = ObjectDict(http_response.data[0])
        else:
            data = http_response.data

    return data


def unboxing_v2(http_response):
    """解析服务返回结果"""

    result = bool(http_response.code == constant.NEWINFRA_API_SUCCESS)
    data = ObjectDict()
    if result:
        data = http_response.data

    return data


def unboxing_v2(http_response):
    """解析服务返回结果"""

    result = bool(http_response.code == constant.NEWINFRA_API_SUCCESS)
    data = ObjectDict()
    if result:
        data = http_response.data or ObjectDict()

    return data


@gen.coroutine
def _async_http_get(route, jdata=None, timeout=5, method='GET', infra=True, headers=None):
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
    if headers and isinstance(headers, dict):
        headers.update({"Content-Type": "application/json"})
    else:
        headers = {"Content-Type": "application/json"}
    logger.debug("[infra][http_{}][url: {}]".format(method.lower(), url))
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        request_timeout=timeout,
        headers=HTTPHeaders(headers)
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

    http_client = tornado.httpclient.AsyncHTTPClient()

    logger.debug(
        "[infra][http_{}][url: {}][body: {}]".format(method.lower(), url, ujson.encode(jdata)))
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


@gen.coroutine
def _v2_async_http_get(route, jdata=None, timeout=5, method='GET'):
    """可用 HTTP 动词为 GET 和 DELETE"""
    if method.lower() not in "get delete":
        raise ValueError("method is not in GET and DELETE")

    if jdata is None:
        jdata = ObjectDict()

    url = url_concat(route, jdata)
    url = params_underline2hump(url)  # 会把url中的请求参数做转换

    http_client = tornado.httpclient.AsyncHTTPClient()
    logger.debug("[newinfra][http_{}][url: {}]".format(method.lower(), url))
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )
    body = json_hump2underline(str(response.body))
    logger.debug("[newinfra][http_{}][url: {}][ret: {}][res_body: {}]".format(
        method.lower(), url, ujson.decode(response.body), body))
    body = ast.literal_eval(body)
    body = objectdictify(ujson.loads(body))

    if body.code in INFRA_ERROR_CODES:
        raise InfraOperationError(body.message)

    return body


@gen.coroutine
def _v2_async_http_post(route, jdata=None, timeout=5, method='POST'):
    """可用 HTTP 动词为 POST, PATCH 和 PUT"""
    if method.lower() not in "post put patch":
        raise ValueError("method is not in POST, PUT and PATCH")

    if jdata is None:
        jdata = ObjectDict()

    jdata = json_underline2hump(ujson.dumps(jdata))
    url = route

    http_client = tornado.httpclient.AsyncHTTPClient()
    logger.debug(
        "[newinfra][http_{}][url: {}][body: {}]".format(method.lower(), url, ujson.encode(jdata)))
    response = yield http_client.fetch(
        url,
        method=method.upper(),
        body=jdata,
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )

    body = json_hump2underline(str(response.body))
    logger.debug(
        "[newinfra][http_{}][url: {}][body: {}][ret: {}][res_body: {}]"
            .format(method.lower(), url, ujson.encode(jdata),
                    ujson.decode(response.body), body))
    body = ast.literal_eval(body)
    body = objectdictify(ujson.loads(body))
    if body.code in INFRA_ERROR_CODES:
        raise InfraOperationError(body.message)

    return body
