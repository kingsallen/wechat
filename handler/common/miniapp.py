# coding=utf-8

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response


class MiniappCodeHandler(BaseHandler):
    """
    获取微信信息
    """

    @handle_response
    @gen.coroutine
    def get(self):
        scene_id = self.params.scene or 1
        buffer = yield self.wechat_ps.get_miniapp_code(scene_id=scene_id)
        self.send_json_success(data={"miniapp_code": buffer})
