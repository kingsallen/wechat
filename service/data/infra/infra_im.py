from tornado import gen

from conf.newinfra_service_conf.service_info import user_service
from conf.newinfra_service_conf.user import user
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.date_tool import curr_now_minute, curr_now
from util.tool.http_tool import http_get_v2, http_post_v2


class InfraImDataService(DataService):
    """
    员工候选人IM数据操作接口
    1. 分页查找聊天室记录
    2. 分页查找消息记录
    3. 离开聊天室
    4. 进入聊天室
    5. 获取未读消息数量
    6. 保存消息记录
    7. 删除聊天室
    8. 获取消息推送开关状态
    9. 改变消息推送的开关状态
    """

    @gen.coroutine
    def get_rooms(self, user_id, role, employee_id, company_id, page_no = 1, page_size = 200):
        """
        获取聊天室列表
        :param user_id: 用户编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :param page_no: 页码
        :param page_size: 每页数量
        :return: 聊天室列表
        """

        params = ObjectDict({
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "page_no": page_no,
            "page_size": page_size,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_ROOMS.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_room(self, room_id, role):
        """
        获取聊天室详情
        :param room_id 聊天室编号
        :param role 角色
        :return: 聊天室列表
        """

        params = ObjectDict({
            "room_id": room_id,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_ROOM.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_messages(self, room_id, user_id, role, employee_id, company_id, page_size=200, message_id = 0):
        """
        分页获取获取聊天记录
        :param room_id: 聊天室编号
        :param user_id: 用户编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :param page_size: 每页数量
        :param message_id: message_id 消息编号。查找的列表是这个消息编号之前的历史消息。如果第一次进入聊天室，message_id = 0
        :return: 聊天消息列表
        """

        params = ObjectDict({
            "room_id" : room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "page_size": page_size,
            "message_id": message_id,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_MESSAGES.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def count_unread_message(self, room_id, role, user_id, employee_id, company_id):
        """
        获取未读聊天消息数量
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id:  用户编号
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :return: 未读消息数量
        """

        params = ObjectDict({
            "room_id": room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_UNREAD_COUNT.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def enter_the_room(self, room_id, role, user_id, employee_id, company_id, position_id):
        """
        进入聊天室
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id: 用户编号
        :param employee_id:  员工编号
        :param company_id: 公司编号
        :param position_id: 职位
        :return: 操作结果
        """

        params = ObjectDict({
            "room_id": room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "position_id": position_id
        })

        ret = yield http_post_v2(user.INFRA_GET_CHATTING_ENTER_THE_ROOM.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def leave_the_room(self, room_id, role, user_id, employee_id, company_id, position_id):
        """
        离开聊天室
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id: 用户编号
        :param employee_id:  员工编号
        :param company_id: 公司编号
        :param position_id: 职位
        :return: 操作结果
        """

        params = ObjectDict({
            "room_id": room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "position_id": position_id
        })

        ret = yield http_post_v2(user.INFRA_GET_CHATTING_LEAVE_THE_ROOM.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_message(self, room_id, role, user_id, employee_id, company_id, content):
        """
        保存消息
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id: 用户编号
        :param employee_id:  员工编号
        :param company_id: 公司编号
        :param content: 消息内容
        :return: 操作结果
        """

        params = ObjectDict({
            "room_id": room_id,
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "message": {
                "content": content,
                "createTime": curr_now(),
                "msgType": "text",
                "speaker": 1 if role == "employee" else 2
            }
        })

        ret = yield http_post_v2(user.INFRA_GET_CHATTING_LEAVE_THE_ROOM.format(role=role), user_service,
                                 params)
        raise gen.Return(ret)

    @gen.coroutine
    def delete_room(self, user_id, role, employee_id, company_id):
        """
        删除聊天室
        :param user_id: 用户编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :return: 操作结果
        """

        params = ObjectDict({
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_DELETE_THE_ROOM.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_switch(self, role, user_id, employee_id, company_id):
        """
        获取消息推送开关状态
        :param role: 角色
        :param user_id: 用户编号
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :return: 开关状态
        """

        params = ObjectDict({
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
        })

        ret = yield http_get_v2(user.INFRA_GET_CHATTING_SWITCH.format(role=role), user_service, params)
        raise gen.Return(ret)

    @gen.coroutine
    def post_switch(self, role, user_id, employee_id, company_id, tpl_switch=False):
        """
        改变消息推送的开关状态
        :param role: 角色
        :param user_id: 用户编号
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :param tpl_switch: 消息推送开关状态。True表示开启推送；False表示关闭消息推送
        :return: 开关状态
        """

        params = ObjectDict({
            "employee_id": employee_id,
            "user_id": user_id,
            "company_id": company_id,
            "tpl_switch": tpl_switch
        })

        ret = yield http_post_v2(user.INFRA_GET_CHATTING_SWITCH.format(role=role), user_service, params)
        raise gen.Return(ret)
