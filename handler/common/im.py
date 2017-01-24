# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated


class UnreadCountHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self, publisher):

        if publisher:
            # JD页未读消息
            chat_num = yield self.im_ps.get_unread_chat_num(self.current_user.sysuser.id, publisher)
            self.send_json_success(data=chat_num)

        else:
            # 侧边栏我的消息未读消息数
            chat_num = yield self.im_ps.get_all_unread_chat_num(self.current_user.sysuser.id)
            self.send_json_success(data=chat_num)
