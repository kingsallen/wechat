# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response, authenticated


class IndexHandler(BaseHandler):
    """页面Index, 单页应用使用"""

    @handle_response
    @gen.coroutine
    def get(self, method='default'):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, 'get_' + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @gen.coroutine
    def get_default(self):

        self.render(template_name="system/app.html")

    @handle_response
    @authenticated
    @gen.coroutine
    def get_usercenter(self):
        """个人中心，需要使用authenticated判断是否登录，及静默授权"""

        self.render(template_name="system/app.html")
