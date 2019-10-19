from tornado import gen

from conf.newinfra_service_conf.service_info import user_service
from conf.newinfra_service_conf.user import user
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get_v2


class InfraIMDataService(DataService):
    """
    员工候选人IM数据操作接口
    1. 分页查找聊天室记录
    2. 分页查找消息记录
    """

    @gen.coroutine
    def get_rooms(self, user_id, role, employee_id, company_id, page_no = 1, page_size = 200):
        """获取聊天室列表"""

        params = ObjectDict({
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "page_no": page_no,
            "page_size": page_size,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_ROOMS.format(role=role), user_service.service_name, params)
        raise gen.Return(ret.data)

    @gen.coroutine
    def get_messages(self, room_id, user_id, role, employee_id, company_id, page_no=1, page_size=200):
        """分页获取获取聊天记录"""

        params = ObjectDict({
            "room_id" : room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "page_no": page_no,
            "page_size": page_size,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_MESSAGES.format(role=role), user_service.service_name, params)
        raise gen.Return(ret.data)

    @gen.coroutine
    def count_unread_message(self, room_id, role, user_id, employee_id, company_id):
        """分页获取获取聊天记录"""

        params = ObjectDict({
            "room_id": room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_UNREAD_COUNT.format(role=role), user_service.service_name, params)
        raise gen.Return(ret.data)
