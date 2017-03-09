# coding=utf-8

from tornado import gen, websocket, escape, ioloop, web
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
        self.set_nodelay(True)
        self.redis_client = self.redis.get_raw_redis_client()
        self.io_loop = ioloop.IOLoop.current()

        self.ping_interval = 2
        self.ping_message = b'p'
        self.ping_timeout = None

        self.chatroom_channel = ''

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

        self.chatroom_channel = chatroom_channel

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

    def on_message(self, message):
        message_body = escape.linkify(message)
        self.redis_client.publish(self.chatroom_channel, message_body)
        # TODO save message to db, async


# import tornado.ioloop
# from tornado import websocket, gen
#
# from tornado.testing import gen_test, AsyncHTTPTestCase
# class TestPingPong(AsyncHTTPTestCase):
#
#     def get_app(self):
#         return get_tornado_app()
#
#     def tearDown(self):
#         tornado.ioloop.IOLoop.instance().stop()
#
#     def setUp(self):
#         super().setUp()
#
#     def test_http_on_ws(self):
#         response = self.fetch('/')
#         self.assertTrue(response.code, 400)
#
#     @gen_test(timeout=15)
#     def test_ping_pong(self):
#
#         url = 'ws://localhost:%d/' % self.get_http_port()
#
#         ws = yield websocket.websocket_connect(url, io_loop=self.io_loop)
#         msg = yield ws.read_message()
#
#         self.assertEqual(msg, 'OK')
#         yield gen.sleep(12)
