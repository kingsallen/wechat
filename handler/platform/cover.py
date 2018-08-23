# coding=utf-8


from tornado import gen

from handler.metabase import MetaBaseHandler


class CoverHandler(MetaBaseHandler):
    """在移动端非微信环境时默认跳转该页面"""

    @gen.coroutine
    def get(self):
        self.render(template_name="adjunct/not-weixin.html")
