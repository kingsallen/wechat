# coding=utf-8

from tornado import gen, websocket, escape
from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
from util.tool.pubsub_tool import Subscriber
import traceback

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


class ChatWebSocketHandler(BaseHandler, websocket.WebSocketHandler):

    def __init__(self):
        self.super().__init__()
        self.redis_client = self.redis.get_raw_redis_client()

    def open(self, chatroom_channel):
        self.chatroom_channel = chatroom_channel

        def message_handler(message):
            nonlocal self
            try:
                self.write_message(message['data'])
            except websocket.WebSocketClosedError:
                self.logger.error(traceback.format_exc())
                raise

        self.subscriber = Subscriber(self.redis_client, self.chatroom_channel,
                                     message_handler=message_handler)
        self.subscriber.start_run_in_thread()

        message_body = self.current_user.sysuser.name + " joined."
        self.redis_client.publish(chatroom_channel, message_body)

    def on_close(self):
        self.subscriber.stop_run_in_thread()
        self.subscriber.cleanup()

    def on_message(self, message):
        message_body = escape.linkify(message)
        self.redis_client.publish(self.chatroom_channel, message_body)
