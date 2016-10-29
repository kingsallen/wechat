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
            self.logger.debug("single")
            chat_num = yield self.im_ps.get_unread_chat_num(self.current_user.sysuser.id, publisher)
            self.logger.debug("chat_num: %s" % chat_num)
            self.send_json_success(data=chat_num)

        else:
            self.logger.debug("ALL")

            # 侧边栏我的消息未读消息数
            chat_num = yield self.im_ps.get_all_unread_chat_num(self.current_user.sysuser.id)
            self.send_json_success(data=chat_num)

