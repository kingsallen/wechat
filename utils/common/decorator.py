# -*- coding: utf-8 -*-

import functools

from tornado import gen

import conf.common as constant


def handle_response_error(method):

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

    return wrapper