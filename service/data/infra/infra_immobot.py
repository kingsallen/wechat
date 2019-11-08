from tornado import gen

from conf.newinfra_service_conf.im import im_mobot
from conf.newinfra_service_conf.service_info import im_service
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get_v2, http_put_v2


class InfraImmobotDataService(DataService):

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
    def user_enter_chatroom(self, room_id, user_id, hr_id, position_id, is_qx_wechat):
        """
        用户进入聊天室
        curl -X PUT 'http://api-t2.dqprism.com/im/v4/user/room/enter?interfaceid=A11037001&appid=A11037&roomId=30780&userId=5399884&hrId=82752&positionId=0&isQxWechat=false'
        """
        params = ObjectDict({
            "roomId": room_id,
            "userId": user_id,
            "hrId": hr_id,
            "positionId": position_id,
            "isQxWechat": is_qx_wechat,
        })

        ret = yield http_put_v2(im_mobot.USER_ENTER_CHATROOM, im_service, params, timeout=5)
        raise gen.Return(ret)
