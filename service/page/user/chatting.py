# coding=utf-8

from tornado import gen

from conf.common import COMPANY_SWITCH_MODULE_CHATTING, NEWINFRA_API_SUCCESS
from service.page.base import PageService

class ChattingPageService(PageService):
    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_employee_chatrooms(self, user_id, role, employee_id, company_id, page_no, page_size):
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

        ret = yield self.infra_im_ds.get_rooms(user_id, role, employee_id, company_id, page_no, page_size)
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee_chatroom(self, room_id, role):
        """
        获取聊天室详情
        :param room_id 聊天室编号
        :param role 角色
        :return: 聊天室列表
        """

        ret = yield self.infra_im_ds.get_room(room_id, role)
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee_chatting_messages(self, room_id, user_id, role, employee_id, company_id, page_size, message_id):
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

        ret = yield self.infra_im_ds.get_messages(room_id, user_id, role, employee_id, company_id, page_size,
                                                  message_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee_chatting_unread_count(self, room_id, role, user_id, employee_id, company_id):
        """
        获取未读聊天消息数量
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id:  用户编号
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :return: 未读消息数量
        """

        ret = yield self.infra_im_ds.count_unread_message(room_id, role, user_id, employee_id, company_id)
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

        ret = yield self.infra_im_ds.get_switch(role, user_id, employee_id, company_id)
        raise gen.Return(ret)

    @gen.coroutine
    def get_chatting_switch(self, company_id, employee):
        """
        获取聊天开关的状态
        :param company_id: 公司编号
        :param employee: 员工身份
        :return: 开关状态
        """

        on = 0
        ret = yield self.infra_im_ds.get_chatting_switch(company_id, COMPANY_SWITCH_MODULE_CHATTING)

        if ret and ret.code and (ret.code == NEWINFRA_API_SUCCESS):
            if ret.data:
                on = 2

        hr_chat_switch = yield self.infra_company_ds.get_hr_chat_switch_status(company_id, '9')
        if hr_chat_switch:
            on = on | 1

        return on

    @gen.coroutine
    def post_switch(self, role, user_id, employee_id, company_id, tpl_switch):
        """
        关闭消息推送
        :param role: 角色
        :param user_id: 用户编号
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :param tpl_switch 开关
        :return: 开关状态
        """

        ret = yield self.infra_im_ds.post_switch(role, user_id, employee_id, company_id, tpl_switch)
        raise gen.Return(ret)

    @gen.coroutine
    def enter_the_room(self, room_id, role, user_id, employee_id, company_id, position_id, entry_type):
        """
        进入聊天室
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id: 用户编号
        :param employee_id:  员工编号
        :param company_id: 公司编号
        :param position_id: 职位
        :param entry_type: 场景
        :return: 操作结果
        """

        ret = yield self.infra_im_ds.enter_the_room(room_id, role, user_id, employee_id, company_id, position_id,
                                                    entry_type)
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

        ret = yield self.infra_im_ds.leave_the_room(room_id, role, user_id, employee_id, company_id, position_id)
        raise gen.Return(ret)

    @gen.coroutine
    def delete_room(self, room_id, role, user_id, employee_id, company_id):
        """
        删除聊天室
        :param room_id: 聊天室编号
        :param user_id: 用户编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param employee_id: 员工编号
        :param company_id: 公司编号
        :return: 操作结果
        """

        ret = yield self.infra_im_ds.delete_room(room_id, user_id, role, employee_id, company_id)
        raise gen.Return(ret)

    @gen.coroutine
    def post_message(self, room_id, role, user_id, employee_id, company_id, content, msg_type, chat_time):
        """
        保存消息
        :param room_id: 聊天室编号
        :param role: 角色 employee是员工进入聊天室；user是候选人进入聊天室
        :param user_id: 用户编号
        :param employee_id:  员工编号
        :param company_id: 公司编号
        :param content: 消息内容
        :param msg_type: 消息类型
        :param chat_time: 消息发送时间
        :return: 操作结果
        """

        ret = yield self.infra_im_ds.post_message(room_id, role, user_id, employee_id, company_id, content, msg_type,
                                                  chat_time)
        raise gen.Return(ret)

    @gen.coroutine
    def post_invite_message(self, company_id, employee_id, position_id, user_id, entry_type, psc):
        """
        通知后端发送模板消息
        :param company_id: 公司编号
        :param employee_id: 员工编号
        :param position_id: 职位编号
        :param user_id: 用户编号
        :param entry_type: 来源
        :param psc: 分享链路编号
        :return: 操作结果
        """

        ret = yield self.infra_im_ds.post_invite_message(company_id, employee_id, position_id, user_id, entry_type, psc)
        raise gen.Return(ret)
