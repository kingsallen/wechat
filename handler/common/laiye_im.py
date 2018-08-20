# coding=utf-8
from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated


class LaiyeImHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """来也js sdk页面渲染
        """
        user_id = self.params.user_id
        pubkye = self.params.pubkey

        self.render_page(
            template_name="adjunct/wulai-im.html",
            data=dict(
                user_id=user_id,
                pubkye=pubkye
            )
        )
