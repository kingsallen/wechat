# coding=utf-8

# Copyright 2016 MoSeeker

import functools
import hashlib

from tornado import gen
from tornado.locks import Semaphore
from tornado.web import MissingArgumentError

import conf.common as constant
from util.common import ObjectDict
from util.common.cache import BaseRedis


def handle_response(func):

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):

        try:
            yield func(self, *args, **kwargs)
        except Exception as e:
            self.logger.error(e)
            if self.request.headers.get("Accept", "").startswith("application/json"):
                self.send_json({
                    "msg": constant.RESPONSE_FAILED,
                }, status_code=416)
            else:
                self.write_error(500)
                return
    return wrapper


base_cache = BaseRedis()
sem = Semaphore(1)
def cache(prefix=None, key=None, ttl=60, hash=True, lock=True, separator=":"):
    """
    cache装饰器

    :param prefix: 指定prefix
    :param key: 指定key
    :param ttl: ttl (s)
    :param hash: 是否需要hash
    :param lock: -
    :param separator: key 分隔符
    :return:
    """
    key_ = key
    ttl_ = ttl
    hash_ = hash
    lock_ = lock
    prefix_ = prefix
    separator_ = separator

    def cache_inner(func):

        key, ttl, hash, lock, prefix, separator = key_, ttl_, hash_, lock_, prefix_, separator_

        prefix = prefix if prefix else "{0}:{1}".format(func.__module__.split(".")[-1], func.__name__)

        @functools.wraps(func)
        @gen.coroutine
        def func_wrapper(*args, **kwargs):

            if lock:
                yield sem.acquire()

            try:
                if not key:

                    redis_key = None

                    if args and len(args) > 1:
                        redis_key = separator.join([str(_) for _ in list(args[1].values())])

                    if kwargs:
                        spliter = separator if redis_key else ""
                        redis_key = redis_key + spliter + separator.join([str(_) for _ in list(kwargs.values())])
                else:
                     redis_key = key

                if hash:
                    redis_key = hashlib.md5(redis_key.encode("utf-8")).hexdigest()

                redis_key = "{prefix}{separator}{redis_key}".format(prefix=prefix, separator=separator, redis_key=redis_key)

                if base_cache.exists(redis_key):
                    cache_data = base_cache.get(redis_key)
                else:
                    cache_data = yield func(*args, **kwargs)
                    base_cache.set(redis_key, cache_data, ttl)

                raise gen.Return(cache_data)

            finally:
                if lock:
                    sem.release()

        return func_wrapper

    return cache_inner


def check_signature(func):
    """如果当前环境是企业号但是url query 没有 wechat_signature, 返回 404

    此装饰器用来装饰 tornado.web.RequestHandler 异步方法，
    如：prepare
    """
    @gen.coroutine
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.is_platform:
            key = "wechat_signature"
            try:
                self.get_query_argument(key, strip=True)
            except MissingArgumentError:
                self.write_error(status_code=404)
            else:
                yield func(self, *args, **kwargs)
    return wrapper


# def url_valid(func):
#     """
#     # 装置环境,包括 wechat, qxuser, wxuser, company, recom, employee
#     :param func:
#     :return:
#     """
#
#     @functools.wraps(func)
#     @gen.coroutine
#     def wrapper(self, *args, **kwargs):
#
#         try:
#             if not getattr(self, "_current_user", None):
#                 self._current_user = yield self.get_current_user()
#                 self._current_user = ObjectDict(self._current_user)
#             yield func(self, *args, **kwargs)
#
#         except Exception as e:
#             self.logger.error(e)
#             return
#     return wrapper
