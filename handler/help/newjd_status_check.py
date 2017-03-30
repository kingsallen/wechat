# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 陈迪（chendi@moseeker.com）
:date 2017.03.28
"""

from tornado import gen
import conf.common as constant
from util.tool import url_tool
from util.tool.url_tool import make_url
from util.common import ObjectDict
from abc import ABCMeta
from abc import abstractmethod
import functools
import re


# 检查新JD状态, 如果不是启用状态, 当前业务规则:
# 1. JD --> 跳老页面
# 2. Company --> 跳老页面
# 3. TeamIndex --> 404
# 4. TeamDetail --> 404

class BaseNewJDStatusChecker(metaclass=ABCMeta):
    def __init__(self):
        self._handler = None

    def __call__(self, func):
        @functools.wraps(func)
        @gen.coroutine
        def wrapper(handler, *args, **kwargs):
            self._handler = handler
            # 新JD开启状态
            is_newjs_status_on = handler.current_user.company.conf_newjd_status == constant.NEWJD_STATUS_ON
            # 预览状态
            is_preview = handler.current_user.company.conf_newjd_status == constant.NEWJD_STATUS_WAITING \
                         and handler.params.preview != None
            if not (is_newjs_status_on or is_preview):
                self.fail_action(*args, **kwargs)
                return

            handler.logger.debug('NewJD status check successful: {}'.format(handler.current_user.wechat.id))
            yield func(handler, *args, **kwargs)

        return wrapper

    @abstractmethod
    def fail_action(self, *args, **kwargs):
        pass


class NewJDStatusChecker404(BaseNewJDStatusChecker):
    '''
    JD status不对应, 直接404
    '''

    def fail_action(self, *args, **kwargs):
        handler = self._handler
        handler.logger.debug(
            'NewJD status check fail, uri: {}, wechat_id: {}'.format(handler.request.uri,
                                                                     handler.current_user.wechat.id))
        handler.write_error(404)


class NewJDStatusCheckerRedirect(BaseNewJDStatusChecker):
    '''
    JD status不对应, 则根据redirect_mapping到重定向到对应页面
    '''

    redirect_mapping = {  # from(new): to(old)

        # Job Detail, 职位详情页
        r"/m/position/([0-9]+)": ObjectDict({
            "url": "/mobile/position",
            "extra": ObjectDict({
                "m": "info"
            }),
            "field_mapping": ObjectDict({
                "position_id": "pid"
            })
        }),

        # CompanyProfile, 公司页
        r"/m/company": ObjectDict({
            "url": "/mobile/position",
            "extra": ObjectDict({
                "m": "company"
            }),
            "field_mapping": ObjectDict({})
        }),

        # Position List, 职位列表页面, 都在老微信
    }

    def fail_action(self, *args, **kwargs):

        handler = self._handler
        handler.logger.debug('NewJD status check fail, redirect, uri: {}, wechat_id: {}'.format(handler.request.uri,
                                                                                                handler.current_user.wechat.id))
        from_path = handler.request.path
        from_url = handler.request.uri

        cloned_params = handler.params
        cloned_params.update(kwargs)
        to = self._get_match(handler.params, from_url)
        handler.logger.debug("to: {}".format(to))

        if to:
            to_path = self.make_url_with_m(to, cloned_params)
            handler.logger.debug('redirect from path: {}, to: {}'.format(from_path, to_path))
            handler.redirect(to_path)
        else:
            handler.write_error(404)

    def _get_match(self, cloned_params, from_url):
        any_matched = [value for key, value in self.redirect_mapping.items() if re.match(key, from_url)]
        if any_matched:
            assert len(any_matched) == 1
            matched = any_matched[0]
            field_mapping = matched.field_mapping
            if field_mapping:
                mapped = ObjectDict({})
                for from_key, to_key in field_mapping.items():
                    mapped[to_key] = cloned_params.get(from_key)
                    cloned_params.pop(from_key)
                matched.extra.update(mapped)
            return matched
        else:
            return None

    @staticmethod
    def make_url_with_m(to, params):
        _OLD_ESCAPE_DEFAULT = url_tool._ESCAPE_DEFAULT
        url_tool._ESCAPE_DEFAULT = set(_OLD_ESCAPE_DEFAULT) - {'m'}
        url = make_url(to.url, params, **to.extra)
        url_tool._ESCAPE_DEFAULT = _OLD_ESCAPE_DEFAULT
        return url


if __name__ == "__main__":
    to = ObjectDict({'extra': {'m': 'company'}, 'field_mapping': {}, 'url': '/mobile/position'})
    params = ObjectDict({'wechat_signature': 'YWNkNmIyYWExOGViOTRkODMyMzk5N2MxM2NkZDZlOTUxNmRjYzJiYQ=='})
    print(NewJDStatusCheckerRedirect.make_url_with_m(to, params))
    print(url_tool._ESCAPE_DEFAULT)
