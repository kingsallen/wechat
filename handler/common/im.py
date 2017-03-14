# coding=utf-8

import ujson
import traceback
from tornado import gen, websocket, ioloop, web

import conf.common as const
import conf.message as msg
from handler.base import BaseHandler
from cache.user.chat_session import ChatCache
from util.common.decorator import handle_response, authenticated
from util.tool.json_tool import json_dumps
from util.tool.pubsub_tool import Subscriber
from util.common import ObjectDict
from util.tool.str_tool import to_str, match_session_id
from util.tool.date_tool import curr_now_minute
from service.page.user.chat import ChatPageService


class UnreadCountHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, publisher):

        try:

            if publisher:
                self._event = self._event + "jdunread"
                yield getattr(self, "get_jd_unread")(publisher)
            else:
                self._event = self._event + "totalunread"
                yield getattr(self, "get_unread_total")()
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


class ChatWebSocketHandler(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(ChatWebSocketHandler, self).__init__(application, request, **kwargs)
        self.redis_client = self.application.redis.get_raw_redis_client()
        self.io_loop = ioloop.IOLoop.current()

        # self.ping_interval = 2
        # self.ping_message = b'p'
        # self.ping_timeout = None

        self.chat_session = ChatCache()
        self.chatroom_channel = ''
        self.hr_channel = ''
        self.room_id = 0
        self.user_id = 0
        self.hr_id = 0
        self.position_id = 0
        self.chat_ps = ChatPageService()

    # TODO
    # def _send_ping(self):
    #     self.ping(self.ping_message)
    #     self.ping_timeout = self.io_loop.call_later(
    #         delay=self.ping_interval,
    #         callback=self._connection_timeout
    #     )
    # def on_pong(self, data):
    #     print (3)
    #
    #     if hasattr(self, 'ping_timeout'):
    #         # clear timeout set by for ping pong (heartbeat) messages
    #         self.io_loop.remove_timeout(self.ping_timeout)
    #
    #         # send new ping message after `get_ping_timeout` time
    #     self.ping_timeout = self.io_loop.call_later(
    #         delay=self.get_ping_timeout(),
    #         callback=self._send_ping,
    #     )
    #
    # def _connection_timeout(self):
    #     """ If no pong message is received within the timeout
    #     then close the connection """
    #     self.close(1001, 'ping-pong timeout')

    def open(self, room_id, *args, **kwargs):

        # self.ping_timeout = self.io_loop.call_later(
        #     delay=self.get_ping_timeout(initial=True),
        #     callback=self._send_ping,
        # )
        self.set_nodelay(True)

        self.room_id = room_id
        self.user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        self.hr_id = self.get_argument("hr_id")
        self.position_id = self.get_argument("pid", 0) or 0

        if not (self.user_id and self.hr_id and self.room_id):
            self.close(1000, "not authorized")

        self.chatroom_channel = const.CHAT_CHATROOM_CHANNEL.format(self.hr_id, self.user_id)
        self.hr_channel = const.CHAT_HR_CHANNEL.format(self.hr_id)
        self.chat_session.mark_enter_chatroom(self.user_id)

        def message_handler(message):
            # 处理 sub 接受到的消息
            nonlocal self
            try:
                print ("-----------")
                print (777777)
                print (message)
                print (type(message))
                data = ujson.loads(message.get("data"))
                if data:
                    self.write_message(json_dumps(ObjectDict(
                        content=data.get("content"),
                        chat_time=data.get("create_time"),
                        speaker=data.get("speaker"),
                    )))
            except websocket.WebSocketClosedError:
                self.logger.error(traceback.format_exc())
                self.close(1002)
                raise

        print ("---")
        print (self.chatroom_channel)
        self.subscriber = Subscriber(self.redis_client, channel=self.chatroom_channel,
                                     message_handler=message_handler)
        self.subscriber.start_run_in_thread()

    @gen.coroutine
    def on_close(self):
        print (444)
        self.subscriber.stop_run_in_thread()
        self.subscriber.cleanup()

        self.chat_session.mark_leave_chatroom(self.user_id)
        yield self.chat_ps.leave_chatroom(self.room_id)

    @gen.coroutine
    def on_message(self, message):
        # 处理通过 websocket 发送的消息
        print ("++++++++++")
        print (888)
        print (message)
        message = ujson.loads(message)
        message_body = json_dumps(ObjectDict(
            content = message.get("content"),
            speaker = 0,
            cid = self.room_id,
            pid = self.position_id,
            create_time = curr_now_minute()
        ))
        print (message_body)
        print (self.hr_channel)
        self.redis_client.publish(self.hr_channel, message_body)
        yield self.chat_ps.save_chat(self.room_id, message.get("content"), self.position_id,)


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
    def get_messages(self):
        """获得指定聊天室的聊天历史记录"""

        if not self.params.room_id:
            self.send_json_error(message=msg.REQUEST_PARAM_ERROR)
            return

        page_no = self.params.page_no or 0
        page_size = self.params.page_size or 10

        # res = yield self.chat_ps.get_chatrooms(self.params.room_id, page_no, page_size)
        res = list()
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

        res = ObjectDict({
            "hr": {
                "hr_id": 1,
                "hr_name": "HR",
                "hr_headimg": self.static_url(const.HR_HEADIMG),
            },
            "user": {
                "user_id": 1,
                "user_name": "用户",
                "user_headimg": self.static_url(const.SYSUSER_HEADIMG),
            },
            "position":{
                "pid": 3,
                "title": "职位标题",
                "company_name": "公司名称",
                "city": "杭州",
                "salary": "面议",
                "update_time": "刚刚",
            },
            "follow_qx": True,
            "room_id": 5,
        })

        # res = yield self.chat_ps.get_chatroom(self.current_user.sysuser.id, self.params.hr_id, pid, room_id, self.current_user.qxuser)
        self.send_json_success(data=res)
