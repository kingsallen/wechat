from tornado import gen

from conf.newinfra_service_conf.im import im_mobot
from conf.newinfra_service_conf.service_info import im_service
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get_v2


class InfraImmobotDataService(DataService):

    @gen.coroutine
    def get_user_chatroom_page(self, user_id, page_no=1, page_size=20):
        """
        获取聊天室列表
        """
        params = ObjectDict({
            "sysuserId": user_id,
            "currentPage": page_no,
            "pageSize": page_size,
        })

        ret = yield http_get_v2(im_mobot.GET_USER_CHATROOM_PAGE, im_service, params)
        raise gen.Return(ret)
