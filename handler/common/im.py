# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
import conf.message as message
from util.common.decorator import handle_response, authenticated


class UnreadCountHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, publisher):

        if publisher:
            # JD页未读消息
            if self.current_user.sysuser.id is None:
                self.send_json_success(data=1)
                raise gen.Return()

            chat_num = yield self.im_ps.get_unread_chat_num(self.current_user.sysuser.id, publisher)
            self.send_json_success(data=chat_num)

        else:
            # 侧边栏我的消息未读消息数
            if self.current_user.sysuser.id is None:
                self.send_json_error(message=message.NOT_AUTHORIZED)
                raise gen.Return()
            chat_num = yield self.im_ps.get_all_unread_chat_num(self.current_user.sysuser.id)
            self.send_json_success(data=chat_num)
