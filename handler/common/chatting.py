# coding=utf-8
import html
import traceback
import ujson

import redis
from tornado import gen, websocket, ioloop

import conf.common as const
from conf.message import CHATTING_EMPLOYEE_RESIGNATION, CHATTING_EMPLOYEE_RESIGNATION_TIPS
from conf.protocol import WebSocketCloseCode
from conf.sensors import CHATTING_SEND_MESSAGE
from globals import logger
from globals import sa
from handler.base import BaseHandler
from service.data.hr.hr_company import HrCompanyDataService
from service.page.user.chatting import ChattingPageService
from service.page.user.user import UserPageService
from setting import settings
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.tool.date_tool import curr_now
from util.tool.json_tool import json_dumps
from util.tool.pubsub_tool import Subscriber
from util.tool.str_tool import to_str, match_session_id


class ChattingRoomsHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        """
        聊天界面。页面由前端同学提供
        :return: 聊天页面
        """
        # 确保页面中用到的post请求的api接口cookie中设置了_xsrf
        self.xsrf_token
        self.render_page(template_name='chat/room.html', data={})


class EmployeeChattingHandler(BaseHandler):
    """
    员工候选人聊天室
    """

    def __init__(self, application, request, **kwargs):
        super(EmployeeChattingHandler, self).__init__(application, request, **kwargs)

        self.role = ""
        self.employee_id = 0
        self.user_id = 0

    @handle_response
    @gen.coroutine
    def get(self, method):

        if self.params.speaker == "1" or self.params.speaker == 1:
            # 当前是员工，获取与候选人的聊天室列表
            self.role = "employee"
            self.employee_id = int(self.params.employee_id or 0)
            self.user_id = int(self.params.user_id or 0)
        elif self.params.speaker == "0" or self.params.speaker == 0:
            # 当前用户是普通的候选人，获取公众号所属公司下员工的聊天室列表
            self.role = "user"
            self.employee_id = int(self.params.employee_id or 0)
            self.user_id = int(self.params.user_id or 0)
        else:
            if self.current_user.employee:
                self.role = "employee"
            else:
                self.role = "user"
        if self.employee_id == 0 and self.current_user.employee:
            self.employee_id = self.current_user.employee.id or 0

        if self.user_id == 0 and not self.current_user.employee:
            self.user_id = self.current_user.sysuser.id or 0

        self.logger.debug("EmployeeChattingHandler get params role:{}, employee_id:{}, user_id:{}"
                          .format(self.role, self.employee_id, self.user_id))

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, "get_" + method)()
        except Exception as e:
            self.write_error(404)

    @authenticated
    @gen.coroutine
    def get_index(self):
        """
        聊天界面。页面由前端同学提供
        :return: 聊天页面
        """
        # 确保页面中用到的post请求的api接口cookie中设置了_xsrf
        self.xsrf_token
        self.render(template_name='chat/room.html')

    @handle_response
    @gen.coroutine
    def post(self, method):

        if self.json_args.get("speaker") == "1" or self.json_args.get("speaker") == 1:
            # 当前是员工，获取与候选人的聊天室列表
            self.role = "employee"
            self.employee_id = int(self.json_args.get("employee_id") or 0)
            self.user_id = int(self.json_args.get("user_id") or 0)
        elif  self.json_args.get("speaker") == "0" or self.json_args.get("speaker") == 0:
            # 当前用户是普通的候选人，获取公众号所属公司下员工的聊天室列表
            self.role = "user"
            self.employee_id = int(self.json_args.get("employee_id") or 0)
            self.user_id = int(self.json_args.get("user_id") or 0)
        else:
            if self.current_user.employee:
                self.role = "employee"
            else:
                self.role = "user"

        if self.employee_id == 0 and self.current_user.employee:
            self.employee_id = self.current_user.employee.id or 0

        if self.user_id == 0 and not self.current_user.employee:
            self.user_id = self.current_user.sysuser.id or 0

        self.logger.debug("EmployeeChattingHandler get params role:{}, employee_id:{}, user_id:{}"
                          .format(self.role, self.employee_id, self.user_id))

        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, "post_" + method)()
        except Exception as e:
            self.write_error(404)

    def un_box(self, ret):
        """
        处理基础服务的返回的数据结构
        :param ret: 基础服务返回的数据结构
        :return: json
        """

        if ret and ret.code and (ret.code == "0" or ret.code == 0):
            self.send_json_success(ret.data)
        else:
            self.send_json_error(ret.data, ret.message)

    @handle_response
    @gen.coroutine
    def get_rooms(self):
        """
        获取聊天室列表
        :return: 聊天室列表
        """

        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10
        self.logger.debug("EmployeeChattingHandler get_rooms user_id:{}, role:{}, employee_id:{}, company_id:{}, "
                          "page_no:{}, page_size:{}".format(self.user_id, self.role, self.employee_id,
                                                            self.current_user.company.id, page_no, page_size))
        if self.role == "employee" and self.employee_id == 0:
            self._send_json(data={}, status_code=30500, message=CHATTING_EMPLOYEE_RESIGNATION_TIPS, http_code=200)
            return
        ret = yield self.chatting_ps.get_employee_chatrooms(self.user_id, self.role, self.employee_id,
                                                            self.current_user.company.id, page_no, page_size)
        self.logger.debug("EmployeeChattingHandler get_rooms ret:{}".format(ret))
        self.un_box(ret)

    @handle_response
    @gen.coroutine
    def get_messages(self):
        """
        获取聊天记录
        :return: 聊天记录
        """

        page_size = self.params.page_size or 10
        message_id = self.params.message_id or 0
        ret = yield self.chatting_ps.get_employee_chatting_messages(self.params.room_id, self.user_id, self.role,
                                                                    self.employee_id, self.current_user.company.id,
                                                                    page_size, message_id)
        if ret and ret.data and ret.data.current_page_data:
            for data in ret.data.current_page_data:
                if data.get("compound_content"):
                    data["compound_content"] = ujson.loads(data.get("compound_content"))

        self.un_box(ret)

    @handle_response
    @gen.coroutine
    def get_unread(self):
        """
        获取聊天室列表
        :return: 聊天室列表
        """
        ret = yield self.chatting_ps.get_employee_chatting_unread_count(self.params.room_id or 0, self.role,
                                                                        self.user_id, self.employee_id,
                                                                        self.current_user.company.id)
        if ret and ret.code and (ret.code == "0" or ret.code == 0):
            self.send_json_success({"unread": ret.data})
        else:
            self.send_json_error({"unread": ret.data}, ret.message)

    @handle_response
    @gen.coroutine
    def get_totalunread(self):
        """
        获取聊天室列表
        :return: 聊天室列表
        """
        self.logger.debug("EmployeeChattingHandler get_totalunread room_id:{}, role:{}, user_id:{}, employee_id:{}, "
                          "company_id:{}"
                          .format(self.params.room_id,
                                  self.role,
                                  self.user_id,
                                  self.employee_id,
                                  self.current_user.company.id)
                          )
        ret = yield self.chatting_ps.get_employee_chatting_unread_count(self.params.room_id or 0, self.role,
                                                                        self.user_id, self.employee_id,
                                                                        self.current_user.company.id)
        self.logger.debug("EmployeeChattingHandler get_totalunread ret:{}".format(ret))
        chat_num = yield self.chat_ps.get_all_unread_chat_num(self.current_user.sysuser.id)
        self.logger.debug("EmployeeChattingHandler get_totalunread chat_num:{}".format(chat_num))

        if ret and ret.code and (ret.code == "0" or ret.code == 0):
            self.logger.debug("EmployeeChattingHandler get_totalunread unread:{}".format(ret.data +
                                                                                         (chat_num if chat_num else 0)))
            self.send_json_success({"unread": ret.data + (chat_num if chat_num else 0)})
        else:
            self.logger.debug("EmployeeChattingHandler get_totalunread unread:{}"
                              .format((ret.data if ret.data else 0) + (chat_num if chat_num else 0)))
            self.send_json_error({"unread": (ret.data if ret.data else 0) + (chat_num if chat_num else 0)}, ret.message)

    @handle_response
    @gen.coroutine
    def get_switch(self):
        """
        获取推送开关
        :return: 推送开关状态
        """

        switch = yield self.chatting_ps.get_switch(self.role, self.user_id, self.employee_id, self.current_user.company.id)
        self.un_box(switch)

    @handle_response
    @gen.coroutine
    def post_switch(self):
        """
        关闭消息推送
        :return: 推送开关状态
        """

        tpl_switch = self.json_args.get("tpl_switch");
        switch = yield self.chatting_ps.post_switch(self.role, self.user_id, self.employee_id, self.current_user.company.id,
                                                    tpl_switch)
        self.un_box(switch)

    @handle_response
    @gen.coroutine
    def post_enter(self):
        """
        进入聊天室
        :return: 推送开关状态
        """
        self.logger.debug("enter room. employee_id:{}, user_id:{}".format(self.employee_id, self.user_id))
        user_id = self.user_id
        employee_id = self.employee_id
        if (self.json_args.get("room_id") and int(self.json_args.get("room_id")) > 0) and (self.user_id == 0 or
                                                                                           self.employee_id == 0):
            room_info = yield self.chatting_ps.get_employee_chatroom(self.json_args.get("room_id"), self.role)
            if room_info and (room_info.code == "0" or room_info.code == 0) and room_info.data:
                user_id = room_info.data.user_id
                employee_id = room_info.data.employee_id

        ret = yield self.chatting_ps.enter_the_room(self.json_args.get("room_id") or 0, self.role, user_id, employee_id,
                                                    self.current_user.company.id, self.json_args.get("pid") or 0)

        if self.role == "employee" and ret and ret.code == "US30500":
            self._send_json(data={}, status_code=30500, message=CHATTING_EMPLOYEE_RESIGNATION_TIPS, http_code=200)
            return
        self.un_box(ret)

    @handle_response
    @gen.coroutine
    def post_rooms(self):
        """
        删除聊天室
        :return: 操作结果
        """
        user_id = self.user_id
        employee_id = self.employee_id
        if (self.json_args.get("room_id") and int(self.json_args.get("room_id")) > 0) and (self.user_id == 0 or
                                                                                           self.employee_id == 0):
            room_info = yield self.chatting_ps.get_employee_chatroom(self.json_args.get("room_id"), self.role)
            if room_info and (room_info.code == "0" or room_info.code == 0) and room_info.data:
                user_id = room_info.data.user_id
                employee_id = room_info.data.employee_id
        ret = yield self.chatting_ps.delete_room(self.json_args.get("room_id") or 0, self.role, user_id, employee_id,
                                                 self.current_user.company.id)
        self.un_box(ret)


class ChattingWebSocketHandler(websocket.WebSocketHandler):
    """
    处理 候选人和员工的聊天的各种 webSocket 传输，直接继承 tornado 的 WebSocketHandler
    """

    def data_received(self, chunk):
        pass

    # todo redis 连接池公用一个
    _pool = redis.ConnectionPool(
        host=settings["chatting_options"]["redis_host"],
        port=settings["chatting_options"]["redis_port"],
        max_connections=settings["chatting_options"]["max_connections"])

    _redis = redis.StrictRedis(connection_pool=_pool)

    _pool_bak = redis.ConnectionPool(
        host=settings["chatting_options"]["redis_host"],
        port=settings["chatting_options"]["redis_port"],
        max_connections=settings["chatting_options"]["max_connections"])

    _redis_bak = redis.StrictRedis(connection_pool=_pool_bak)

    def __init__(self, application, request, **kwargs):
        super(ChattingWebSocketHandler, self).__init__(application, request, **kwargs)
        self.redis_client = self._redis
        self.redis_client_bak = self._redis_bak
        self.chatting_user_channel = ''
        self.chatting_employee_channel = ''
        self.employee_id = 0
        self.room_id = 0
        self.user_id = 0
        self.candidate_id = 0
        self.position_id = 0
        self.speaker = 0
        self.company_id = 0
        self.io_loop = ioloop.IOLoop.current()

        self.chat_ps = ChattingPageService()
        self.employee_ps = UserPageService()
        self.user_ps = UserPageService()
        self.company_ps = HrCompanyDataService()
        self.sa = sa

    @gen.coroutine
    def open(self, room_id, *args, **kwargs):
        logger.debug("------------ start open ChattingWebSocketHandler --------------")
        self.room_id = room_id
        self.user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        self.employee_id = self.get_argument("employee_id")
        self.speaker = int(self.get_argument("speaker", 0))
        self.candidate_id = self.get_argument("user_id", 0)
        self.company_id = self.get_argument("company_id", 0)

        if self.speaker == 1:
            role = "employee"
        else:
            role = "user"

        if room_id and (not self.employee_id or not self.user_id or not self.company_id):
            room_info = yield self.chat_ps.get_employee_chatroom(self.room_id, role)
            logger.debug("ChattingWebSocketHandler open room_info:{}".format(room_info))
            if room_info and (
                room_info.code == "0" or room_info.code == 0) and room_info.data and room_info.data.user_id:
                self.company_id = room_info.data.company_id
                self.employee_id = room_info.data.employee_id
                self.candidate_id = room_info.data.user_id

        self.position_id = self.get_argument("pid", 0)
        self.chatting_user_channel = const.CHAT_CHATTING_CHANNEL.format(self.candidate_id, self.employee_id)
        self.chatting_employee_channel = const.CHAT_CHATTING_CHANNEL.format(self.employee_id, self.candidate_id)

        try:
            assert self.user_id and self.employee_id and self.room_id and self.candidate_id
        except AssertionError:
            self.close(WebSocketCloseCode.normal.value, "not authorized")

        self.set_nodelay(True)
        if self.speaker == 1:
            channel = self.chatting_user_channel
        else:
            channel = self.chatting_employee_channel

        def message_handler(message):
            # 处理 sub 接受到的消息
            nonlocal self
            try:
                data = ujson.loads(message.get("data"))

                logger.debug("ChattingWebSocketHandler data:{}".format(data))
                if data:
                    self.write_message(json_dumps(ObjectDict(
                        content=data.get("content"),
                        compound_content=data.get("compound_content"),
                        create_time=data.get("create_time"),
                        speaker=data.get("speaker"),
                        msg_type=data.get("msg_type"),
                        stats=data.get("stats")
                    )))
                    logger.debug("----------websocket write finish----------")
            except websocket.WebSocketClosedError:
                self.logger.error(traceback.format_exc())
                self.close(WebSocketCloseCode.internal_error.value)
                raise

        logger.debug("---------- ready to subscribe -----------")

        self.subscriber = Subscriber(
            self.redis_client,
            channel=channel,
            message_handler=message_handler)

        logger.debug("------------- subscribe finish ---------------")
        self.subscriber.start_run_in_thread()

    @gen.coroutine
    def on_message(self, message):
        logger.debug("ChattingWebSocketHandler received a message:{}".format(message))
        data = ujson.loads(message)
        if data.get("msg_type") == 'ping':
            self.write_message(ujson.dumps({"msg_type": 'pong'}))
            return

        if data.get("speaker") == 1 or data.get("speaker") == "1":
            role = "employee"
            channel = self.chatting_employee_channel
        else:
            role = "user"
            channel = self.chatting_user_channel

        if self.room_id and int(self.room_id) > 0 and (not self.company_id or self.company_id == 0
                                                       or not self.candidate_id or self.candidate_id == 0
                                                       or not self.employee_id or self.employee_id == 0):
            room_info = yield self.chat_ps.get_employee_chatroom(self.room_id, role)
            if room_info and (room_info.code == "0" or room_info.code == 0) and room_info.data and room_info.data.company_id:
                self.company_id = room_info.data.company_id
                self.candidate_id = room_info.data.user_id
                self.employee_id = room_info.data.employee_id
        create_time = curr_now()
        content = html.escape(data.get('content'))
        chat_id = yield self.chat_ps.post_message(self.room_id, role, self.candidate_id, self.employee_id,
                                                  self.company_id, content, "html", create_time)
        if role == "user" and chat_id and chat_id.code == "US305073":
            try:
                message_body = json_dumps(ObjectDict(
                    msg_type=const.CHATTING_EMPLOYEE_MSG_TYPE_RESIGNATION,
                    content=CHATTING_EMPLOYEE_RESIGNATION,
                    compound_content=None,
                    speaker=1,
                    cid=int(self.room_id),
                    pid=int(self.position_id) if self.position_id else 0,
                    create_time=create_time,
                    id=chat_id.get("data"),
                ))
                self.write_message(message_body)
            except websocket.WebSocketClosedError:
                logger.error(traceback.format_exc())
                self.close(WebSocketCloseCode.internal_error.value)
                raise
            return

        if not chat_id or (chat_id.code != "0" and chat_id.code != 0) or not chat_id.data:
            return

        try:
            message_body = json_dumps(ObjectDict(
                msg_type="msg_id",
                content=chat_id.get("data"),
                compound_content=None,
                speaker=data.get("speaker"),
                cid=int(self.room_id),
                pid=int(self.position_id) if self.position_id else 0,
                create_time=create_time,
                id=chat_id.get("data"),
            ))

            self.write_message(message_body)

        except websocket.WebSocketClosedError:
            logger.error(traceback.format_exc())
            self.close(WebSocketCloseCode.internal_error.value)
            raise

        message_body = json_dumps(ObjectDict(
            msg_type=data.get("msg_type"),
            content=content,
            compound_content=None,
            speaker=data.get("speaker"),
            cid=int(self.room_id),
            pid=int(self.position_id) if self.position_id else 0,
            create_time=create_time,
            id=chat_id.get("data"),
        ))

        logger.debug("ChattingWebSocketHandler publish chat by redis message_body:{}".format(message_body))
        self.redis_client_bak.publish(channel, message_body)

        if data.get("speaker") == 1 or data.get("speaker") == "1":
            employee = yield self.employee_ps.get_employee_by_id(self.employee_id)
            distinct_id = employee.sysuser_id
            is_login_id = True
        else:
            distinct_id = self.candidate_id
            user_user = yield self.user_ps.get_user_user({"id": distinct_id})
            is_login_id = bool(user_user.username.isdigit())

        condition = {'id': self.company_id}
        company_info = yield self.company_ps.get_company(condition)

        properties = ObjectDict({"companyId": company_info.id,
                                "companyName": company_info.abbreviation})

        self.sa.track(distinct_id=distinct_id,
                      event_name=CHATTING_SEND_MESSAGE,
                      properties=properties,
                      is_login_id=is_login_id)

    @gen.coroutine
    def on_close(self):
        self.subscriber.stop_run_in_thread()
        self.subscriber.cleanup()
        if self.speaker == 1:
            role = "employee"
        else:
            role = "user"
        yield self.chat_ps.leave_the_room(self.room_id, role, self.candidate_id, self.employee_id, self.company_id,
                                          self.position_id)

