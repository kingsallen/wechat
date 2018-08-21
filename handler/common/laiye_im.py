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
        pub_key = self.params.pubkey

        self.render(
            template_name="adjunct/wulai-im.html",
            wulai_config=dict(
                pubkey=pub_key,
                fullScreen=True,
                minimize=0,
                autoOpen=False,
                userId=None,
                env='prod',
                async=False,
                userinfo={}
            )
        )
