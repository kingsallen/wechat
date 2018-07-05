# coding=utf-8

import ujson
import traceback
from tornado import gen, websocket, ioloop
import conf.common as const
import conf.message as msg
from conf.protocol import WebSocketCloseCode
from handler.base import BaseHandler
from cache.user.chat_session import ChatCache
from util.common.decorator import handle_response, authenticated
from util.tool.pubsub_tool import Subscriber
from util.common import ObjectDict
from util.tool.str_tool import to_str, match_session_id
from util.tool.date_tool import curr_now_minute
from service.page.user.chat import ChatPageService
from thrift_gen.gen.chat.struct.ttypes import ChatVO
import redis
from setting import settings
from globals import logger
from oauth.wechat import JsApi
from util.tool.json_tool import encode_json_dumps, json_dumps
import conf.message as msg_const


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

        chat_num = yield self.chat_ps.get_unread_chat_num(self.current_user.sysuser.id, publisher)
        if self.is_platform:
            self.send_json_success(data={
                "unread": chat_num,
            })
        else:
            g_event = yield self._get_ga_event(publisher)
            self.send_json_success(data={
                "unread": chat_num,
                "is_subscribe": self.current_user.qxuser.is_subscribe == 1,
                "event": g_event,
                "qrcode": self.current_user.wechat.qrcode
            })

    @handle_response
    @authenticated
    @gen.coroutine
    def get_unread_total(self):
        """
        获得侧边栏用户未读消息总数，需要用户先登录
        :return:
        """

        chat_num = yield self.chat_ps.get_all_unread_chat_num(self.current_user.sysuser.id)
        if self.is_platform:
            self.send_json_success(data={
                "unread": chat_num,
            })
        else:
            g_event = yield self._get_ga_event()
            self.send_json_success(data={
                "unread": chat_num,
                "is_subscribe": self.current_user.qxuser.is_subscribe == 1,
                "event": g_event,
                "qrcode": self.current_user.wechat.qrcode
            })

    @gen.coroutine
    def _get_ga_event(self, publisher=None):
        """
        点击消息按钮类型
        :param publisher:
        :return:
        """

        if publisher:
            hr_info = yield self.chat_ps.get_hr_info(publisher)
            # 是否关闭 IM 聊天，由母公司决定
            company_info = yield self.company_ps.get_company(conds={
                "id": hr_info.company_id
            }, need_conf=True)
        else:
            company_info = self.current_user.company

        g_event = 0
        if not self.in_wechat and not self.current_user.sysuser:
            g_event = 1
        elif not self.in_wechat and self.current_user.sysuser and self.current_user.qxuser.is_subscribe != 1:
            g_event = 2
        elif self.in_wechat and self.current_user.qxuser.is_subscribe != 1:
            g_event = 3
        elif self.current_user.qxuser.is_subscribe == 1 and not company_info.conf_hr_chat:
            g_event = 4
        elif self.current_user.qxuser.is_subscribe == 1 and company_info.conf_hr_chat:
            g_event = 5

        return g_event


class ChatWebSocketHandler(websocket.WebSocketHandler):
    """处理 Chat 的各种 webSocket 传输，直接继承 tornado 的 WebSocketHandler
    """

    _pool = redis.ConnectionPool(
        host=settings["store_options"]["redis_host"],
        port=settings["store_options"]["redis_port"],
        max_connections=settings["store_options"]["max_connections"])

    _redis = redis.StrictRedis(connection_pool=_pool)

    def __init__(self, application, request, **kwargs):
        super(ChatWebSocketHandler, self).__init__(application, request, **kwargs)
        self.redis_client = self._redis
        self.chatroom_channel = ''
        self.hr_channel = ''
        self.hr_id = 0
        self.room_id = 0
        self.user_id = 0
        self.position_id = 0
        self.io_loop = ioloop.IOLoop.current()

        self.chat_session = ChatCache()
        self.chat_ps = ChatPageService()

    def open(self, room_id, *args, **kwargs):

        self.room_id = room_id
        self.user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        self.hr_id = self.get_argument("hr_id")
        self.position_id = self.get_argument("pid", 0) or 0

        try:
            assert self.user_id and self.hr_id and self.room_id
        except AssertionError:
            self.close(WebSocketCloseCode.normal.value, "not authorized")

        self.set_nodelay(True)

        self.chatroom_channel = const.CHAT_CHATROOM_CHANNEL.format(self.hr_id, self.user_id)
        self.hr_channel = const.CHAT_HR_CHANNEL.format(self.hr_id)
        self.chat_session.mark_enter_chatroom(self.room_id)

        def message_handler(message):
            # 处理 sub 接受到的消息
            nonlocal self
            try:
                data = ujson.loads(message.get("data"))
                if data:
                    self.write_message(json_dumps(ObjectDict(
                        content=data.get("content"),
                        chatTime=data.get("createTime"),
                        speaker=data.get("speaker"),
                        assetUrl=data.get("assetUrl"),
                        btnContent=data.get("btnContent"),
                        msgType=data.get("msgType"),
                        duration=data.get("duration") or 0,
                        serverId=data.get("serverId") or 0
                    )))
            except websocket.WebSocketClosedError:
                self.logger.error(traceback.format_exc())
                self.close(WebSocketCloseCode.internal_error.value)
                raise

        self.subscriber = Subscriber(
            self.redis_client,
            channel=self.chatroom_channel,
            message_handler=message_handler)

        self.subscriber.start_run_in_thread()

    @gen.coroutine
    def on_close(self):
        logger.debug("&=! {}".format("on_close, before stop_run_in_thread"))
        self.subscriber.stop_run_in_thread()
        logger.debug("&=! {}".format("on_close, after stop_run_in_thread"))
        logger.debug("&=! {}".format("on_close, before cleanup"))
        self.subscriber.cleanup()
        logger.debug("&=! {}".format("on_close, after cleanup"))

        self.chat_session.mark_leave_chatroom(self.room_id)
        yield self.chat_ps.leave_chatroom(self.room_id)


class ChatRoomHandler(BaseHandler):
    """聊天页面"""

    @gen.coroutine
    def get(self, room_id):
        hr_id = self.params.hr_id or 0
        if hr_id:
            company_id = yield self.company_ps.get_real_company_id(hr_id, self.current_user.company.id)
            wechat = yield self.wechat_ps.get_wechat(conds={
                "company_id": company_id
            })
            jsapi_ticket = wechat.jsapi_ticket
            appid = wechat.appid
        else:
            jsapi_ticket = self.current_user.wechat.jsapi_ticket
            appid = self.current_user.wechat.appid

        jsapi = JsApi(
            jsapi_ticket=jsapi_ticket, url=self.fullurl(encode=False))

        config = ObjectDict({
            "debug": False,
            "appid": appid,
            "timestamp": jsapi.timestamp,
            "nonceStr": jsapi.nonceStr,
            "signature": jsapi.signature,
            "jsApiList": ["onMenuShareTimeline",
                          "onMenuShareAppMessage",
                          "onMenuShareQQ",
                          "onMenuShareWeibo",
                          "hideOptionMenu",
                          "showOptionMenu",
                          "startRecord",
                          "stopRecord",
                          "onVoiceRecordEnd",
                          "playVoice",
                          "pauseVoice",
                          "stopVoice",
                          "onVoicePlayEnd",
                          "uploadVoice",
                          "translateVoice",
                          "downloadVoice",
                          "hideMenuItems",
                          "showMenuItems",
                          "hideAllNonBaseMenuItem",
                          "showAllNonBaseMenuItem"]
        })
        self.logger.debug("jsapi_config:{}".format(config))
        self._render(
            template_name="chat/room.html",
            data={"room_id": room_id},
            config=config
        )

    @gen.coroutine
    def _render(self, template_name,
                data,
                status_code=const.API_SUCCESS,
                message=msg_const.RESPONSE_SUCCESS,
                meta_title=const.PAGE_META_TITLE,
                http_code=200,
                config=None):
        """render 页面"""
        self.log_info = {"res_type": "html", "status_code": status_code}
        self.set_status(http_code)

        try:
            render_json = encode_json_dumps({
                "status": status_code,
                "message": message,
                "data": data
            })
        except TypeError as e:
            self.logger.error(e)
            render_json = encode_json_dumps({
                "status": const.API_FAILURE,
                "message": msg_const.RESPONSE_FAILURE,
                "data": None
            })
        super().render(
            template_name=template_name,
            render_json=render_json,
            meta_title=meta_title,
            jsapi=config)
        return


class ChatHandler(BaseHandler):
    """聊天相关处理"""

    _pool = redis.ConnectionPool(
        host=settings["store_options"]["redis_host"],
        port=settings["store_options"]["redis_port"],
        max_connections=settings["store_options"]["max_connections"])

    _redis = redis.StrictRedis(connection_pool=_pool)

    def __init__(self, application, request, **kwargs):
        super(ChatHandler, self).__init__(application, request, **kwargs)
        self.redis_client = self._redis
        self.chatroom_channel = ''
        self.hr_channel = ''
        self.hr_id = 0
        self.room_id = 0
        self.user_id = 0
        self.position_id = 0
        self.bot_enabled = False

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

        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10
        res = yield self.chat_ps.get_chatrooms(self.current_user.sysuser.id, page_no, page_size)
        self.send_json_success(data=ObjectDict(
            records=res
        ))

    @handle_response
    @authenticated
    @gen.coroutine
    def get_messages(self):
        """获得指定聊天室的聊天历史记录"""

        if not self.params.room_id:
            self.send_json_error(message=msg.REQUEST_PARAM_ERROR)
            return

        room_info = yield self.chat_ps.get_chatroom_info(self.params.room_id)

        # 需要判断用户是否进入自己的聊天室
        if not room_info or room_info.sysuser_id != self.current_user.sysuser.id:
            self.send_json_error(message=msg.NOT_AUTHORIZED)
            return

        page_no = self.params.page_no or 1
        page_size = self.params.page_size or 10

        res = yield self.chat_ps.get_chats(self.params.room_id, page_no, page_size)
        self.send_json_success(data=ObjectDict(
            records=res
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

        # gamma 项目 hr 欢迎导语不同
        is_gamma = False
        if self.is_qx and int(self.params.hr_id) == int(self.current_user.company.hraccount_id):
            is_gamma = True

        self.logger.debug(
            '[IM]user_id: %s, hr_id: %s, position_id: %s, room_id: %s, qxuser: %s, is_gamma: %s' %
            (self.current_user.sysuser.id, self.params.hr_id, pid, room_id, self.current_user.qxuser, is_gamma)
        )

        res = yield self.chat_ps.get_chatroom(self.current_user.sysuser.id,
                                              self.params.hr_id,
                                              pid, room_id,
                                              self.current_user.qxuser,
                                              is_gamma)
        # 需要判断用户是否进入自己的聊天室
        if res.user.user_id != self.current_user.sysuser.id:
            self.send_json_error(message=msg.NOT_AUTHORIZED)
            return

        # 如果已经开启chatbot聊天，不需要发送职位给hr
        if not self.bot_enabled:
            yield self.get_bot_enabled()

        if self.bot_enabled:
            res.update(show_position_info=False)
        else:
            res.update(show_position_info=True)
        self.send_json_success(data=res)

    @handle_response
    @authenticated
    @gen.coroutine
    def get_voice(self):
        self.user_id = self.current_user.sysuser.id
        server_id = self.params.serverId
        self.room_id = self.params.roomId
        self.hr_id = self.params.hrId
        ret = yield self.chat_ps.get_voice(user_id=self.user_id, server_id=server_id, room_id=self.room_id,
                                           hr_id=self.hr_id)
        voice_file = ret.get("data").get("fileBytes")
        voice_size = ret.get("data").get("fileLength")
        self.set_header("Content-Type", "audio/mp3")
        result = bytes(i % 256 for i in voice_file)
        if len(result) > voice_size:
            voice_size = len(result)
        self.set_header("Content-Length", voice_size)
        self.write(result)
        self.finish()

    @handle_response
    @authenticated
    @gen.coroutine
    def post(self, method):
        try:
            # 重置 event，准确描述
            self._event = self._event + method
            yield getattr(self, "post_" + method)()
        except Exception as e:
            self.write_error(404)

    @handle_response
    @authenticated
    @gen.coroutine
    def get_limit(self):
        hr_id = self.json_args.hrId
        status, message = yield self.chat_ps.chat_limit(hr_id)
        if status == 0:
            self.send_json_success(message=message)
        else:
            self.send_json_error(message=message)

    @handle_response
    @authenticated
    @gen.coroutine
    def post_message(self):

        self.room_id = self.params.roomId
        self.user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        self.hr_id = self.params.hrId
        self.position_id = self.params.get("pid") or 0

        content = self.json_args.get("content")
        user_message = ujson.dumps(content) if type(content) != str else content
        msg_type = self.json_args.get("msgType")
        server_id = self.json_args.get("serverId") or ""
        duration = self.json_args.get("duration") or 0

        if not self.bot_enabled:
            yield self.get_bot_enabled()

        self.chatroom_channel = const.CHAT_CHATROOM_CHANNEL.format(self.hr_id, self.user_id)
        self.hr_channel = const.CHAT_HR_CHANNEL.format(self.hr_id)

        if msg_type == 'html' and not user_message.strip():
            self.send_json_error()
            return
        chat_params = ChatVO(
            msgType=msg_type,
            content=user_message,
            origin=const.ORIGIN_USER_OR_HR,
            roomId=int(self.room_id),
            positionId=int(self.position_id),
            serverId=server_id,
            duration=int(duration)
        )
        chat_id = yield self.chat_ps.save_chat(chat_params)

        message_body = json_dumps(ObjectDict(
            msgType=msg_type,
            content=user_message,
            speaker=const.CHAT_SPEAKER_USER,
            cid=int(self.room_id),
            pid=int(self.position_id),
            createTime=curr_now_minute(),
            origin=const.ORIGIN_USER_OR_HR,
            id=chat_id,
            serverId=server_id,
            duration=duration
        ))

        self.redis_client.publish(self.hr_channel, message_body)
        try:
            if self.bot_enabled and msg_type != "job":
                # 由于没有延迟的发送导致hr端轮训无法订阅到publish到redis的消息　所以这里做下延迟处理
                # delay_robot = functools.partial(self._handle_chatbot_message, user_message)
                # ioloop.IOLoop.current().call_later(1, delay_robot)
                yield self._handle_chatbot_message(user_message)  # 直接调用方式
        except Exception as e:
            self.logger.error(e)

        self.send_json_success()

    @gen.coroutine
    def _handle_chatbot_message(self, user_message):
        """处理 chatbot message
        获取消息 -> pub消息 -> 入库
        """
        bot_message = yield self.chat_ps.get_chatbot_reply(
            message=user_message,
            user_id=self.user_id,
            hr_id=self.hr_id,
            position_id=self.position_id
        )
        if bot_message.msg_type == '':
            return
        chat_params = ChatVO(
            content=bot_message.content,
            speaker=const.CHAT_SPEAKER_HR,
            origin=const.ORIGIN_CHATBOT,
            assetUrl=bot_message.pic_url,
            btnContent=bot_message.btn_content_json,
            msgType=bot_message.msg_type,
            roomId=int(self.room_id),
            positionId=int(self.position_id)
        )

        chat_id = yield self.chat_ps.save_chat(chat_params)
        if bot_message:
            message_body = json_dumps(ObjectDict(
                content=bot_message.content,
                assetUrl=bot_message.pic_url,
                btnContent=bot_message.btn_content,
                msgType=bot_message.msg_type,
                speaker=const.CHAT_SPEAKER_HR,
                cid=int(self.room_id),
                pid=int(self.position_id),
                createTime=curr_now_minute(),
                origin=const.ORIGIN_CHATBOT,
                id=chat_id
            ))
            # hr 端广播
            self.redis_client.publish(self.hr_channel, message_body)

            # 聊天室广播
            self.redis_client.publish(self.chatroom_channel, message_body)

    @gen.coroutine
    def get_bot_enabled(self):

        if not self.hr_id:
            return

        user_hr_account = yield self.chat_ps.get_hr_info(self.hr_id)

        company_id = user_hr_account.company_id

        if not company_id:
            return

        company_conf = yield self.chat_ps.get_company_conf(company_id)

        self.bot_enabled = company_conf.hr_chat == const.COMPANY_CONF_CHAT_ON_WITH_CHATBOT and user_hr_account.leave_to_mobot
