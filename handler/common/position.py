# coding=utf-8

from tornado import gen

from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated

class PositionStarHandler(BaseHandler):
    """处理收藏（加星）操作"""

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self):
        try:
            self.guarantee('star', 'pid')
        except:
            raise gen.Return()

        # 收藏操作
        if self.params.star:
            ret = yield self.user_ps.favorite_position(
                self.current_user, self.params.pid)
        else:
            ret = yield self.user_ps.unfavorite_position(
                self.current_user, self.params.pid)

        if ret:
            self.send_json_success()
        else:
            self.send_json_error()
