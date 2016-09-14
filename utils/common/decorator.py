# coding=utf-8

# Copyright 2016 MoSeeker

import functools

from tornado import gen
from tornado.util import ObjectDict

import conf.common as constant


def handle_response(method):

    @functools.wraps(method)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):

        try:
            yield method(self, *args, **kwargs)
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

def handle_env(func):

    """
    # 装置环境,包括 wechat, qxuser, wxuser, company, recom, employee
    :param func:
    :return:
    """

    @functools.wraps(func)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):

        try:
            if not getattr(self, "_current_user", None):
                self._current_user = yield self.get_current_user()
                self._current_user = ObjectDict(self._current_user)
            yield func(self, *args, **kwargs)

        except Exception, e:
            self.logger.error(e)
            return
    return wrapper
