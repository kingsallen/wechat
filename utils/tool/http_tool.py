# -*- coding: utf-8 -*-

"""
api 调用工具类，
调用时使用 infra=True/False 来选择使用 das 还是基础服务的 api
"""

import ujson
import requests

import tornado.httpclient
from tornado import gen
from tornado.httputil import url_concat, HTTPHeaders

import settings


def http_get(route, jdata, infra=False):
    """
    适合V2的接口返回，如果数据正确，直接返回data数据，业务方不需要再解析response结构
    """
    response = requests.get(
        "{0}/{1}".format(settings.infra if infra else settings.das, route),
        params=jdata).json()

    if response and response.get('status') == 0:
        return response.get('data')
    else:
        return response


def http_post(route, jdata, infra=False):
    """
    适合V2的接口返回，如果数据正确，直接返回data数据，业务方不需要再解析response结构
    """
    response = requests.post(
        "{0}/{1}".format(settings.infra if infra else settings.das, route),
        data=jdata).json()

    if response and response.get('status') == 0:
        return response.get('data')
    else:
        return response


@gen.coroutine
def async_http_get(route, jdata, timeout=8, infra=False):
    """
    适合V2的接口返回，如果数据正确，直接返回data数据，业务方不需要再解析response结构
    """
    url = url_concat("{0}/{1}".format(
        settings.infra if infra else settings.das, route), jdata)

    http_client = tornado.httpclient.AsyncHTTPClient()

    response = yield http_client.fetch(
        url, request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"}))

    body = ujson.loads(response.body)
    content_type = response.headers.get('Content-Type', '')

    if body.get('status') == 0 and "application/json" in content_type:
        raise gen.Return(body.get('data'))
    raise gen.Return(body)


@gen.coroutine
def async_http_post_v2(route, jdata, timeout=8, infra=False,
                       method='POST'):
    """
    适合V2的接口返回，如果数据正确，直接返回data数据，业务方不需要再解析response结构
    method 默认为 POST, 但是也可以用其他的 HTTP 方法
    不要使用 GET, 以及其它非 HTTP 动词
    """
    if method.lower() not in "post put delete patch":
        raise ValueError("{method} is not a valid HTTP verb".format(
            method.lower()))

    http_client = tornado.httpclient.AsyncHTTPClient()

    url = "{0}/{1}".format(settings.infra if infra else settings.das,
                           route)

    response = yield http_client.fetch(
        url,
        method=method.upper(),
        body=ujson.dumps(jdata),
        request_timeout=timeout,
        headers=HTTPHeaders({"Content-Type": "application/json"})
    )

    body = ujson.loads(response.body)
    content_type = response.headers.get('Content-Type', '')

    if body.get('status', 1) == 0 and "application/json" in content_type:
        raise gen.Return(body.get('data'))
    raise gen.Return(body)
