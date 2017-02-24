# coding=utf-8

from tornado import gen
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated


class UnreadCountHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, publisher):

        try:

            if publisher:
                yield getattr(self, "get_jd_unread")(publisher)
                self._event = self._event + "jdunread"
            else:
                yield getattr(self, "get_unread_total")()
                self._event = self._event + "totalunread"
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def get_jd_unread(self, publisher):
        """
        获得 JD 页未读消息数，未登录用户返回默认值1
        :param publisher:
        :return:
        """

        chat_num = yield self.im_ps.get_unread_chat_num(self.current_user.sysuser.id, publisher)
        self.send_json_success(data=chat_num)

    @authenticated
    @handle_response
    @gen.coroutine
    def get_unread_total(self):
        """
        获得侧边栏用户未读消息总数，需要用户先登录
        :return:
        """

        chat_num = yield self.im_ps.get_all_unread_chat_num(self.current_user.sysuser.id)
        self.send_json_success(data=chat_num)
