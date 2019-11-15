from tornado import gen

from conf.newinfra_service_conf.im import im_mobot
from conf.newinfra_service_conf.service_info import im_service
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.date_tool import curr_now
from util.tool.http_tool import http_get_v2, http_post_v2, http_put_v2, http_delete_v2


class InfraImmobotDataService(DataService):

    @gen.coroutine
    def get_user_allchatroom_unread(self, user_id):
        """
        获取聊天室信息
        curl -X GET 'http://api-t2.dqprism.com/im/v4/user/room/unread?interfaceid=A11037001&appid=A11037&sysuserId=123&hraccountId=1'
        """
        params = ObjectDict({
            "sysuserId": user_id,
        })
        ret = yield http_get_v2(im_mobot.GET_USER_ALLCHATROOM_UNREAD, im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def get_user_chatroom_info(self, user_id, hr_id):
        """
        获取聊天室信息
        curl -X GET 'http://api-t2.dqprism.com/im/v4/user/room/info?interfaceid=A11037001&appid=A11037&sysuserId=123&hraccountId=1'
        """
        params = ObjectDict({
            "sysuserId": user_id,
            "hraccountId": hr_id,
        })
        ret = yield http_get_v2(im_mobot.GET_USER_CHATROOM_INFO, im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def get_user_chatroom_page(self, user_id, page_no=1, page_size=20):
        """
        获取聊天室列表
        curl -X GET 'http://api-t2.dqprism.com/im/v4/user/room/page?interfaceid=A11037001&appid=A11037&sysuserId=123&pageSize=20&currentPage=1'
        """
        params = ObjectDict({
            "sysuserId": user_id,
            "currentPage": page_no,
            "pageSize": page_size,
        })

        ret = yield http_get_v2(im_mobot.GET_USER_CHATROOM_PAGE, im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def user_enter_chatroom(self, mobot_type_key, room_id, user_id, hr_id, position_id, is_qx_wechat):
        """
        用户进入聊天室
        curl -X PUT 'http://api-t2.dqprism.com/im/v4/user/room/enter?interfaceid=A11037001&appid=A11037&roomId=30780&userId=5399884&hrId=82752&positionId=0&isQxWechat=false'
        """
        room_type_dict = {'social': 1, 'campus': 2, 'employee': 3}

        params = ObjectDict({
            "roomId": room_id,
            "userId": user_id,
            "hrId": hr_id,
            "positionId": position_id,
            "isQxWechat": is_qx_wechat,
            "roomType": room_type_dict[mobot_type_key]
        })

        ret = yield http_put_v2(im_mobot.USER_ENTER_CHATROOM, im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def user_leave_chatroom(self, room_id, user_id, speaker=0):
        """
        用户离开聊天室
        curl -X PUT 'http://api-t2.dqprism.com/im/v4/user/room/leave?interfaceid=A11037001&appid=A11037&roomId=30780&userId=5399884&hrId=82752&positionId=0&isQxWechat=false'
        """
        params = ObjectDict({
            "roomId": room_id,
            "userId": user_id,
            "leaveTime": curr_now(),
            "speaker": speaker,
        })

        ret = yield http_put_v2(im_mobot.USER_LEAVE_CHATROOM, im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def user_delete_chatroom(self, room_id, user_id):
        """
        用户离开聊天室
        curl -X DELETE 'http://api-t2.dqprism.com/im/v4/user/room/{roomId}?interfaceid=A11037001&appid=A11037'
        """
        params = ObjectDict({
            "sysuserId": user_id,
        })

        ret = yield http_delete_v2(im_mobot.USER_DELETE_CHATROOM.format(room_id), im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def get_user_chat_history_record_page(self, room_id, user_id, page_no=1, page_size=20):
        """
        获取用户聊天历史记录分页数据
        curl -X GET 'http://api-t2.dqprism.com/im/v4/user/room/30780/history/page?interfaceid=A11037001&appid=A11037&sysuserId=5399884&hraccountId=82752&pageSize=20&currentPage=1'
        """
        params = ObjectDict({
            "sysuserId": user_id,
            "currentPage": page_no,
            "pageSize": page_size,
        })
        route = im_mobot.GET_USER_CHAT_HISTORY_RECORD_PAGE.format(room_id=room_id)
        ret = yield http_get_v2(route, im_service, params, timeout=5)
        raise gen.Return(ret)

    @gen.coroutine
    def save_chat_record(self, company_id, room_id, user_id, msg_type, origin, pid, content, compound_content, speaker,
                         voice_server_id, voice_duration):
        """
        保存聊天内容
        curl -X POST 'http://api-t2.dqprism.com/im/v4/user/room/30780/chat/content?interfaceid=A11037001&appid=A11037'
        """
        params = ObjectDict({
            "companyId": company_id,
            "chatlistId": room_id,
            "sysuserId": user_id,
            "msgType": msg_type,
            "content": content,
            "compoundContent": compound_content,
            "speaker": speaker,
            "origin": origin,
            "createTime": curr_now(),
            "pid": pid,
            "duration": voice_duration or 0,
            "serverId": voice_server_id or 0
        })
        route = im_mobot.SAVE_CHAT_RECORD.format(room_id=room_id)
        ret = yield http_post_v2(route, im_service, params, timeout=5)
        raise gen.Return(ret)
