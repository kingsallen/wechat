# coding=utf-8

import traceback
from tornado import gen, websocket, escape, ioloop

import conf.common as const
import conf.message as msg
from handler.base import BaseHandler
from cache.user.chat_session import ChatCache
from util.common.decorator import handle_response, authenticated
from util.tool.pubsub_tool import Subscriber
from util.common import ObjectDict


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

    @handle_response
    @authenticated
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
        self.set_nodelay(True)
        self.redis_client = self.redis.get_raw_redis_client()
        self.io_loop = ioloop.IOLoop.current()

        self.ping_interval = 2
        self.ping_message = b'p'
        self.ping_timeout = None

        self.chatroom_channel = ''
        self.chat_session = ChatCache()
        self.room_id = 0

    def _send_ping(self):
        self.ping(self.ping_message)
        self.ping_timeout = self.io_loop.call_later(
            delay=self.ping_interval,
            callback=self._connection_timeout
        )

    def on_pong(self, data):
        if hasattr(self, 'ping_timeout'):
            # clear timeout set by for ping pong (heartbeat) messages
            self.io_loop.remove_timeout(self.ping_timeout)

            # send new ping message after `get_ping_timeout` time
        self.ping_timeout = self.io_loop.call_later(
            delay=self.get_ping_timeout(),
            callback=self._send_ping,
        )

    def _connection_timeout(self):
        """ If no pong message is received within the timeout
        then close the connection """
        self.close(1001, 'ping-pong timeout')

    def open(self, chatroom_channel, *args, **kwargs):
        self.ping_timeout = self.io_loop.call_later(
            delay=self.get_ping_timeout(initial=True),
            callback=self._send_ping,
        )

        self.room_id = self.params.room_id

        if not (self.current_user.sysuser.id and self.params.hr_id and self.room_id):
            self.close(1000, "not authorized")

        self.chatroom_channel = const.CHAT_CHATROOM_CHANNEL.format(self.params.hr_id, self.current_user.sysuser.id)
        self.chat_session.mark_enter_chatroom(self.current_user.sysuser.id)

        def message_handler(message):
            nonlocal self
            try:
                self.write_message(message['data'])
            except websocket.WebSocketClosedError:
                self.logger.error(traceback.format_exc())
                self.close(1002)
                raise

        self.subscriber = Subscriber(self.redis_client, self.chatroom_channel,
                                     message_handler=message_handler)
        self.subscriber.start_run_in_thread()

        self.redis_client.publish(chatroom_channel, 'OK')

    def on_close(self):
        self.subscriber.stop_run_in_thread()
        self.subscriber.cleanup()

        yield self.chat_ps.leave_chatroom(self.room_id)
        self.chat_session.mark_leave_chatroom(self.current_user.sysuser.id)

    def on_message(self, message):
        message_body = escape.linkify(message)
        self.redis_client.publish(self.chatroom_channel, message_body)
        # TODO save message to db, async


class ChatHandler(BaseHandler):
    """聊天相关处理"""

    @handle_response
    @gen.coroutine
    def get(self, method):

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, "get_" + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @authenticated
    @gen.coroutine
    def get_chatrooms(self):
        """获得 C 端用户的聊天室列表"""

        page_no = self.params.page_no or 0
        page_size = self.params.page_size or 10
        res = yield self.chat_ps.get_chatrooms(self.current_user.sysuser.id, page_no, page_size)
        self.send_json_success(data=ObjectDict(
            records = res
        ))

    @handle_response
    @authenticated
    @gen.coroutine
    def get_chats(self):
        """获得指定聊天室的聊天历史记录"""

        if not self.params.room_id:
            self.send_json_error(message=msg.REQUEST_PARAM_ERROR)
            return

        page_no = self.params.page_no or 0
        page_size = self.params.page_size or 10

        res = yield self.chat_ps.get_chatrooms(self.params.room_id, page_no, page_size)
        self.send_json_success(data=ObjectDict(
            records = res
        ))

    @handle_response
    @authenticated
    @gen.coroutine
    def get_room(self):
        """进入聊天室"""

        if not self.params.hr_id:
            self.send_json_error(message=msg.REQUEST_PARAM_ERROR)
            return
        pid = self.params.pid or 0
        room_id = self.params.room_id or 0
        res = yield self.chat_ps.get_chatroom(self.current_user.sysuser.id, self.params.hr_id, pid, self.current_user.qxuser, room_id)
        self.send_json_success(data=res)
