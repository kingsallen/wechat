# coding=utf-8

import traceback
from urllib.parse import unquote

import redis
import ujson
import time
from tornado import gen, websocket, ioloop

import conf.common as const
import conf.message as msg
import conf.message as msg_const
from cache.user.chat_session import ChatCache
from conf.protocol import WebSocketCloseCode
from globals import logger
from handler.base import BaseHandler
from oauth.wechat import JsApi
from service.page.user.chat import ChatPageService
from setting import settings
from thrift_gen.gen.chat.struct.ttypes import ChatVO
from util.common import ObjectDict
from util.common.decorator import handle_response, authenticated
from util.common.decorator import relate_user_and_former_employee
from util.tool.date_tool import curr_now_minute
from util.tool.json_tool import encode_json_dumps, json_dumps
from util.tool.pubsub_tool import Subscriber
from util.tool.str_tool import to_str, match_session_id


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
        logger.debug("------------ start open websocket --------------")
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
                logger.debug("websocket data:{}".format(data))
                if data:
                    self.write_message(json_dumps(ObjectDict(
                        content=data.get("content"),
                        compoundContent=data.get("compoundContent"),
                        chatTime=data.get("createTime"),
                        speaker=data.get("speaker"),
                        msgType=data.get("msgType"),
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
            channel=self.chatroom_channel,
            message_handler=message_handler)
        logger.debug("------------- subscribe finish ---------------")
        self.subscriber.start_run_in_thread()

    @gen.coroutine
    def on_message(self, message):
        logger.debug("[websocket] received a message:{}".format(message))
        data = ujson.loads(message)
        if data.get("msgType") == 'ping':
            self.write_message(ujson.dumps({"msgType": 'pong'}))

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

    @relate_user_and_former_employee
    @authenticated
    @gen.coroutine
    def get(self, room_id):

        # MoBot页面跳转 platform老的地址：/m/chat/room -> /m/mobot
        if room_id:
            self.params['room_id'] = room_id

        to = self.make_url('/mobot', self.params)
        self.redirect(to)

        return

        # hr_id = self.params.hr_id or 0
        # if hr_id:
        #     company_id = yield self.company_ps.get_real_company_id(hr_id, self.current_user.company.id)
        #     wechat = yield self.wechat_ps.get_wechat(conds={
        #         "company_id": company_id,
        #         "authorized": const.YES
        #     })
        #     jsapi_ticket = wechat.jsapi_ticket
        #     appid = wechat.appid
        # else:
        #     jsapi_ticket = self.current_user.wechat.jsapi_ticket
        #     appid = self.current_user.wechat.appid
        #
        # jsapi = JsApi(
        #     jsapi_ticket=jsapi_ticket, url=self.fullurl(encode=False))
        #
        # res_privacy, data_privacy = yield self.privacy_ps.if_privacy_agreement_window(
        #     self.current_user.sysuser.id)
        #
        # config = ObjectDict({
        #     "debug": False,
        #     "appid": appid,
        #     "timestamp": jsapi.timestamp,
        #     "nonceStr": jsapi.nonceStr,
        #     "signature": jsapi.signature,
        #     "jsApiList": ["onMenuShareTimeline",
        #                   "onMenuShareAppMessage",
        #                   "updateTimelineShareData",
        #                   "updateAppMessageShareData",
        #                   "onMenuShareQQ",
        #                   "updateTimelineShareData",
        #                   "updateAppMessageShareData",
        #                   "onMenuShareWeibo",
        #                   "hideOptionMenu",
        #                   "showOptionMenu",
        #                   "startRecord",
        #                   "stopRecord",
        #                   "onVoiceRecordEnd",
        #                   "playVoice",
        #                   "pauseVoice",
        #                   "stopVoice",
        #                   "onVoicePlayEnd",
        #                   "uploadVoice",
        #                   "translateVoice",
        #                   "downloadVoice",
        #                   "hideMenuItems",
        #                   "showMenuItems",
        #                   "hideAllNonBaseMenuItem",
        #                   "showAllNonBaseMenuItem"]
        # })
        # self.logger.debug("jsapi_config:{}".format(config))
        # self._render(
        #     template_name="chat/room.html",
        #     data={
        #         "room_id": room_id,
        #         "show_privacy_agreement": bool(data_privacy)
        #     },
        #     config=config
        # )

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

    # 这里的聊天使用redis有问题，请不要在其他地方使用这个redis连接池
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
        self.flag = 0
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
    def get_environ(self):
        """
        获取当前环境信息，jssdk config & current_user & locale_code

        @:param share_url 当前网页地址的uri
        :return:
        """

        res_privacy, data_privacy = yield self.privacy_ps.if_privacy_agreement_window(
            self.current_user.sysuser.id)

        # data参数前端会被浏览器encode一次，js又会encodeURIComponent一次
        jsapi = JsApi(jsapi_ticket=self.current_user.wechat.jsapi_ticket,
                      url=unquote(self.params.share_url))

        config = ObjectDict({
                  "debug": False,
                  "appid": self.current_user.wechat.appid,
                  "timestamp": jsapi.timestamp,
                  "nonceStr": jsapi.nonceStr,
                  "signature": jsapi.signature,
                  "jsApiList": [
                                "updateAppMessageShareData",
                                "updateTimelineShareData",
                                "onMenuShareWeibo",
                                "onMenuShareQZone",
                                "startRecord",
                                "stopRecord",
                                "onVoiceRecordEnd",
                                "playVoice",
                                "pauseVoice",
                                "stopVoice",
                                "onVoicePlayEnd",
                                "uploadVoice",
                                "downloadVoice",
                                "chooseImage",
                                "previewImage",
                                "uploadImage",
                                "downloadImage",
                                "translateVoice",
                                "getNetworkType",
                                "openLocation",
                                "getLocation",
                                "hideOptionMenu",
                                "showOptionMenu",
                                "hideMenuItems",
                                "showMenuItems",
                                "hideAllNonBaseMenuItem",
                                "showAllNonBaseMenuItem",
                                "closeWindow",
                                "scanQRCode",
                                "chooseWXPay",
                                "openProductSpecificView",
                                "addCard",
                                "chooseCard",
                                "openCard"
                                ]
        })
        self.logger.debug("get_environ get jssdk config:{}".format(config))

        self.current_user.wechat.jsapi = config

        self.send_json_success(data=ObjectDict(
            locale_code=self.locale.code,
            user=self.current_user,
            env=self.env,
            show_privacy_agreement=bool(data_privacy)
        ))

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
        self.hr_id = self.params.hr_id
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

        # 如果已经开启chatbot聊天，不需要发送职位给hr
        if not self.bot_enabled:
            yield self.get_bot_enabled()

        user_hr_account = yield self.chat_ps.get_hr_info(self.hr_id)
        company_id = user_hr_account.company_id

        recom = self.position_ps._make_recom(self.current_user.sysuser.id)

        is_employee = bool(self.current_user.employee if self.current_user else None)

        res = yield self.chat_ps.get_chatroom(self.current_user.sysuser.id,
                                              self.params.hr_id,
                                              company_id,
                                              pid, room_id,
                                              self.current_user.qxuser,
                                              is_gamma,
                                              self.bot_enabled,
                                              recom,
                                              is_employee)

        # 需要判断用户是否进入自己的聊天室
        if res.user.user_id != self.current_user.sysuser.id:
            self.send_json_error(message=msg.NOT_AUTHORIZED)
            return

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

    def _add_sensor_track(self, msg_type, is_mobot_reply, content):
        """
        神策数据埋点

        source 1:我是员工，2:粉丝智推，3:粉丝完善简历，4:员工智推，5:联系HR，6:申请投递后

        :param msg_type: html, voice
        :param is_mobot_reply: True:需要MoBot回复，False：需要HR回复
        :return:
        """
        properties = ObjectDict({'source': self.params.source or -1,
                                 'distinct_id': self.current_user.sysuser.id,
                                 'company_id': self.current_user.company.id,
                                 'sendTime': int(time.time() * 1000),
                                 'is_mobot_reply': is_mobot_reply,
                                 'msg_type': msg_type,
                                 'content': content
                                 })
        # aiMoBotPostMessageEvent => MoBot页面发送消息事件
        self.track("aiMoBotPostMessageEvent", properties)

    @handle_response
    @authenticated
    @gen.coroutine
    def post_message(self):
        """
        用户chat发送消息响应处理

        @:param flag int(1) 0:社招 1:校招 2:meet mobot, 3:智能推荐, 4:{{data}}, 5: {{decodeURIComponent(data)}}
                scene emp_chat 我是员工
        @:param msgType str(50) 消息类型  ping, pong, html, text, image, voice, job, voice-preview, cards, job-sender,
                                         button_radio, teamSelect, textPlaceholder, satisfaction, textList, citySelect,
                                         industrySelect, positionSelect, jobCard, jobSelect, employeeBind, redirect,
                                         uploadResume
        @:param serverId str(256) 微信语音内容，微信服务器生成的serverId
        @:param duration int(1) 微信语音时长
        @:param create_new_context boolean 是否创建了新的会话
        @:param from_textfield boolean 用户输入内容是否触发脚本非法分支，如触发，终止当前脚本新起脚本（unexpected_branch_allowed）
        @:param compoundContent str(text) 复杂结构体的聊天内容
        @:param content str(text) 用户发送的内容
        @:param pid int(11) 职位ID
        @:param hrId int(11) HRID
        @:param roomId int(11) 聊天室ID

        :return:
        """

        self.room_id = self.params.roomId
        self.user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        self.hr_id = self.params.hrId
        self.position_id = self.params.get("pid") or 0
        self.flag = int(self.params.get("flag")) or None

        content = self.json_args.get("content") or ""
        compoundContent = self.json_args.get("compoundContent") or {}
        user_message = compoundContent or content
        msg_type = self.json_args.get("msgType")
        server_id = self.json_args.get("serverId") or ""
        duration = self.json_args.get("duration") or 0
        create_new_context = self.json_args.get("create_new_context") or False
        from_textfield = self.json_args.get("from_textfield") or False

        self.logger.debug('post_message  flag:{}'.format(self.flag))
        self.logger.debug('post_message  create_new_context:{}'.format(create_new_context))

        if not self.bot_enabled:
            yield self.get_bot_enabled()

        self.chatroom_channel = const.CHAT_CHATROOM_CHANNEL.format(self.hr_id, self.user_id)
        self.hr_channel = const.CHAT_HR_CHANNEL.format(self.hr_id)

        chat_params = ChatVO(
            msgType=msg_type,
            compoundContent=ujson.dumps(compoundContent),
            content=content,
            origin=const.ORIGIN_USER_OR_HR,
            roomId=int(self.room_id),
            positionId=int(self.position_id),
            serverId=server_id,
            duration=int(duration)
        )
        self.logger.debug("save chat by alphadog chat_params:{}".format(chat_params))
        chat_id = yield self.chat_ps.save_chat(chat_params)

        message_body = json_dumps(ObjectDict(
            msgType=msg_type,
            content=content,
            compoundContent=compoundContent,
            speaker=const.CHAT_SPEAKER_USER,
            cid=int(self.room_id),
            pid=int(self.position_id),
            createTime=curr_now_minute(),
            origin=const.ORIGIN_USER_OR_HR,
            id=chat_id,
        ))
        self.logger.debug("publish chat by redis message_body:{}".format(message_body))
        self.redis_client.publish(self.hr_channel, message_body)
        try:
            if self.bot_enabled and msg_type != "job":
                # 由于没有延迟的发送导致hr端轮训无法订阅到publish到redis的消息　所以这里做下延迟处理
                # delay_robot = functools.partial(self._handle_chatbot_message, user_message)
                # ioloop.IOLoop.current().call_later(1, delay_robot)
                yield self._handle_chatbot_message(user_message, create_new_context, from_textfield)  # 直接调用方式
        except Exception as e:
            self.logger.error(e)

        # 添加聊天对话埋点记录
        self._add_sensor_track(msg_type, self.bot_enabled, content)

        self.send_json_success()

    @handle_response
    @authenticated
    @gen.coroutine
    def post_trigger(self):
        self.room_id = self.params.roomId
        self.user_id = match_session_id(to_str(self.get_secure_cookie(const.COOKIE_SESSIONID)))
        self.hr_id = self.params.hrId
        self.position_id = self.params.get("pid") or 0
        self.flag = self.params.get("flag") or 0

        content = self.json_args.get("content") or ""
        compoundContent = self.json_args.get("compoundContent") or {}
        user_message = compoundContent or content
        msg_type = self.json_args.get("msgType")
        create_new_context = self.json_args.get("create_new_context") or False
        from_textfield = self.json_args.get("from_textfield") or False

        self.logger.debug('post_trigger  create_new_context:{}'.format(create_new_context))

        if not self.bot_enabled:
            yield self.get_bot_enabled()

        self.chatroom_channel = const.CHAT_CHATROOM_CHANNEL.format(self.hr_id, self.user_id)
        self.hr_channel = const.CHAT_HR_CHANNEL.format(self.hr_id)

        try:
            if self.bot_enabled and msg_type != "job":
                # 由于没有延迟的发送导致hr端轮训无法订阅到publish到redis的消息　所以这里做下延迟处理
                # delay_robot = functools.partial(self._handle_chatbot_message, user_message)
                # ioloop.IOLoop.current().call_later(1, delay_robot)
                yield self._handle_chatbot_message(user_message, create_new_context, from_textfield)  # 直接调用方式
        except Exception as e:
            self.logger.error(e)

        self.send_json_success()

    @gen.coroutine
    def _handle_chatbot_message(self, user_message, create_new_context, from_textfield):
        """处理 chatbot message
        获取消息 -> pub消息 -> 入库
        """
        social = yield self.company_ps.check_oms_switch_status(
            self.current_user.company.id,
            "社招"
        )
        campus = yield self.company_ps.check_oms_switch_status(
            self.current_user.company.id,
            "校招"
        )
        bot_messages = yield self.chat_ps.get_chatbot_reply(
            current_user=self.current_user,
            message=user_message,
            user_id=self.user_id,
            hr_id=self.hr_id,
            position_id=self.position_id,
            flag=self.flag,
            create_new_context=create_new_context,
            from_textfield=from_textfield,
            social=social['data']['valid'],
            campus=campus['data']['valid']
        )
        self.logger.debug('_handle_chatbot_message  flag:{}'.format(self.flag))
        self.logger.debug('_handle_chatbot_message  social_switch:{}'.format(social['data']['valid']))
        self.logger.debug('_handle_chatbot_message  campus_switch:{}'.format(campus['data']['valid']))
        self.logger.debug('_handle_chatbot_message  create_new_context{}'.format(create_new_context))
        for bot_message in bot_messages:
            msg_type = bot_message.msg_type
            compound_content = bot_message.compound_content
            if bot_message.msg_type == '':
                continue
            if msg_type in const.INTERACTIVE_MSG:
                compound_content.update(disabled=True)  # 可交互类型消息入库后自动标记为不可操作
            if msg_type == "cards":
                # 只在c端展示，并且不保存
                if bot_message:
                    if msg_type in const.INTERACTIVE_MSG:
                        compound_content.update(disabled=False)  # 可交互类型消息发送给各端时需标记为可以操作
                    message_body = json_dumps(ObjectDict(
                        compoundContent=compound_content,
                        content=bot_message.content,
                        msgType=msg_type,
                        speaker=const.CHAT_SPEAKER_HR,
                        cid=int(self.room_id),
                        pid=int(self.position_id),
                        createTime=curr_now_minute(),
                        origin=const.ORIGIN_CHATBOT
                    ))
                    # 聊天室广播
                    self.redis_client.publish(self.chatroom_channel, message_body)
                    return

            # 员工认证自定义配置字段太大了，不用存储到mysql中，直接通过socket发送到客户端即可
            # 特此新起变量处理， 变量compoundContent 只用作save
            if msg_type == "employeeBind":
                compoundContent = ''
            else:
                compoundContent = ujson.dumps(compound_content)

            chat_params = ChatVO(
                compoundContent=compoundContent,
                content=bot_message.content,
                speaker=const.CHAT_SPEAKER_HR,
                origin=const.ORIGIN_CHATBOT,
                msgType=msg_type,
                roomId=int(self.room_id),
                positionId=int(self.position_id),
                stats=ujson.dumps(bot_message.stats),
            )
            self.logger.debug("save chat by alphadog chat_params:{}".format(chat_params))
            chat_id = yield self.chat_ps.save_chat(chat_params)
            if bot_message:
                if msg_type in const.INTERACTIVE_MSG:
                    compound_content.update(disabled=False)  # 可交互类型消息发送给各端时需标记为可以操作
                message_body = json_dumps(ObjectDict(
                    compoundContent=compound_content,
                    content=bot_message.content,
                    stats=bot_message.stats,
                    msgType=msg_type,
                    speaker=const.CHAT_SPEAKER_HR,
                    cid=int(self.room_id),
                    pid=int(self.position_id),
                    createTime=curr_now_minute(),
                    origin=const.ORIGIN_CHATBOT,
                    id=chat_id
                ))
                self.logger.debug("publish chat by redis message_body:{}".format(message_body))
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

        self.bot_enabled = user_hr_account.leave_to_mobot


class MobotHandler(BaseHandler):

    @handle_response
    @authenticated
    @gen.coroutine
    def get(self):
        # 确保页面中用到的post请求的api接口cookie中设置了_xsrf
        self.xsrf_token

        # 添加页面埋点数据
        self._add_sensor_track()

        self.render(template_name='mobot/index.html')

    def _add_sensor_track(self):
        # 神策数据埋点
        # source 1:我是员工，2:粉丝智推，3:粉丝完善简历，4:员工智推，5:联系HR，6:申请投递后
        properties = ObjectDict({'source': self.params.source or -1,
                                 'distinct_id': self.current_user.sysuser.id,
                                 'company_id': self.current_user.company.id,
                                 'sendTime': int(time.time() * 1000)
                                 })
        # aiMoBotPageview => 访问MoBot页面
        self.track("aiMoBotPageview", properties)
