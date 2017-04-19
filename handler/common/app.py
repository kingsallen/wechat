# coding=utf-8

import re
from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response, authenticated


class IndexHandler(BaseHandler):
    """页面Index, 单页应用使用"""

    # 需要静默授权的 path
    _NEED_AUTH_PATHS = ['usercenter', 'employee', 'asist']

    @handle_response
    @gen.coroutine
    def get(self):

        self.logger.debug("IndexHandler request.uri: {}".format(self.request.uri))
        method_list = re.match("\/m\/app\/([a-zA-Z-][a-zA-Z0-9-]*)?.*", self.request.uri)
        self.logger.debug("IndexHandler: {}".format(method_list))
        method = method_list.group(1) if method_list else "default"

        self.logger.debug("IndexHandler: {}".format(method))
        self._save_dqpid_cookie()

        try:
            if method in self._NEED_AUTH_PATHS:
                yield getattr(self, 'get_auth_first')()
            else:
                yield getattr(self, 'get_default')()

            # 重置 event，准确描述
            self._event = self._event + method
            self.logger.debug("IndexHandler event: %s" % self._event)

        except Exception as e:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def get_default(self):
        self.logger.debug("IndexHandler default")
        self.render(template_name="system/app.html")

    @handle_response
    @authenticated
    @gen.coroutine
    def get_auth_first(self):
        """个人中心，需要使用authenticated判断是否登录，及静默授权"""
        self.logger.debug("IndexHandler usercenter")
        self.render(template_name="system/app.html")

    def _save_dqpid_cookie(self):
        """ 新用户在申请职位的时候进入老六步创建简历时
        在 /m/app/profile/new 页面，保存 pid 进 session cookie <dqpid>

        Profile 创建成功后在根据 dqpid 是否存在判断跳转
        """
        if re.match(r"/m/app/profile/new", self.request.uri):
            if self.params.pid:
                self.set_cookie('dqpid', self.params.pid)
                self.logger.debug('dqpid: %s saved' % self.params.pid)
