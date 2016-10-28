# coding=utf-8

from handler.base import BaseHandler

from tornado import gen
from util.common.decorator import handle_response


class UnreadCountHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, publisher):

        self.logger.debug("IM: %s" % publisher)

        if publisher:
            # JD页未读消息
            chat_num = yield self.im_ps.get_unread_chat_num(self.current_user.sysuser.id, publisher)
            chat_num = int(chat_num) if chat_num else 1
            self.send_json_success(data=chat_num)

        else:
            # 侧边栏我的消息未读消息数
            pass

