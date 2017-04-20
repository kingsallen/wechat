# coding=utf-8

# @Time    : 3/10/17 15:15
# @Author  : panda (panyuxin@moseeker.com)
# @File    : chat.py
# @DES     :

from tornado import gen

import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.url_tool import make_static_url
from util.tool.date_tool import str_2_date
from util.tool.str_tool import gen_salary

class ChatPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_chatrooms(self, user_id, page_no, page_size):
        """获得聊天室列表"""

        ret = yield self.thrift_chat_ds.get_chatrooms_list(user_id, page_no, page_size)
        obj_list = list()
        if ret.rooms:
            for e in ret.rooms:
                room = ObjectDict()
                room['id'] = e.id
                room['hr_id'] = e.hrId
                room['hr_name'] = e.name or "HR"
                room['hr_headimg'] = make_static_url(e.headImgUrl or e.companyLogo or const.HR_HEADIMG)
                room['company_name'] = e.companyName
                room['chat_time'] = str_2_date(e.createTime, self.constant.TIME_FORMAT_MINUTE)
                room['unread_num'] = e.unReadNum
                obj_list.append(room)

        self.logger.debug("[get_chatrooms]ret:{}".format(obj_list))
        raise gen.Return(obj_list)

    @gen.coroutine
    def get_chats(self, room_id, page_no, page_size):
        """获得聊天历史记录"""

        ret = yield self.thrift_chat_ds.get_chats(room_id, page_no, page_size)
        obj_list = list()
        if ret.chatLogs:
            for e in ret.chatLogs:
                room = ObjectDict()
                room['id'] = e.id
                room['content'] = e.content
                room['chat_time'] = str_2_date(e.create_time, const.TIME_FORMAT_MINUTE)
                room['speaker'] = e.speaker # 0：求职者，1：HR
                obj_list.append(room)

        self.logger.debug("[get_chats]ret:{}".format(obj_list))
        raise gen.Return(obj_list)

    @gen.coroutine
    def get_chatroom(self, user_id, hr_id, position_id, room_id, qxuser):
        """进入聊天室"""

        ret = yield self.thrift_chat_ds.enter_chatroom(user_id, hr_id, position_id, room_id)

        hr_info = ObjectDict()
        if ret.hr:
            hr_info = ObjectDict(
                hr_id = ret.hr.hrId,
                hr_name = ret.hr.hrName or "HR",
                hr_headimg = make_static_url(ret.hr.hrHeadImg or const.HR_HEADIMG)
            )

        user_info = ObjectDict()
        if ret.user:
            user_info = ObjectDict(
                user_id = ret.user.userId,
                user_name = ret.user.userName,
                user_headimg = make_static_url(ret.user.userHeadImg or const.SYSUSER_HEADIMG)
            )

        position_info = ObjectDict()
        if ret.position:
            position_info = ObjectDict(
                pid = ret.position.positionId,
                title = ret.position.positionTitle,
                company_name = ret.position.companyName,
                city = ret.position.city,
                salary = gen_salary(ret.position.salaryTop, ret.position.salaryBottom),
                update_time = str_2_date(ret.position.updateTime, const.TIME_FORMAT_MINUTE)
            )
        res = ObjectDict(
            hr = hr_info,
            user = user_info,
            position = position_info,
            chat_debut = ret.chatDebut,
            follow_qx = qxuser.is_subscribe == 1,
            room_id = ret.roomId,
        )

        self.logger.debug("[get_chatroom]ret:{}".format(res))

        raise gen.Return(res)

    @gen.coroutine
    def leave_chatroom(self, room_id, speaker=0):
        """
        离开聊天室
        :param room_id:
        :param speaker: 0：求职者，1：HR
        :return:
        """

        ret = yield self.thrift_chat_ds.leave_chatroom(room_id, speaker)
        self.logger.debug("[leave_chatroom]ret:{}".format(ret))
        raise gen.Return(ret)

    @gen.coroutine
    def save_chat(self, room_id, content, position_id, speaker=0):
        """
        记录聊天内容
        :param room_id:
        :param content:
        :param position_id:
        :param speaker: 0：求职者，1：HR
        :return:
        """

        self.logger.debug("save_chat_ps start")
        self.logger.debug("save_chat_ps room_id:{}".format(room_id))
        self.logger.debug("save_chat_ps content:{}".format(content))
        self.logger.debug("save_chat_ps position_id:{}".format(position_id))
        self.logger.debug("save_chat_ps speaker:{}".format(speaker))

        ret = yield self.thrift_chat_ds.save_chat(room_id, content, position_id, speaker)
        self.logger.debug("[save_chat]ret:{}".format(ret))
        raise gen.Return(ret)

    @gen.coroutine
    def get_unread_chat_num(self, user_id, hr_id):

        if user_id is None or not hr_id:
            raise gen.Return(1)

        """返回JD 页，求职者与 HR 之间的未读消息数"""
        chatroom_unread_count = yield self.hr_chat_unread_count_ds.get_chat_unread_count(conds={
            "user_id": user_id,
            "hr_id": hr_id
        })

        # 若无聊天，则默认显示1条未读消息
        if not chatroom_unread_count:
            raise gen.Return(1)

        raise gen.Return(chatroom_unread_count.user_unread_count)

    @gen.coroutine
    def get_all_unread_chat_num(self, user_id):

        """返回求职者所有的未读消息数，供侧边栏我的消息未读消息提示"""

        if user_id is None:
            raise gen.Return(0)

        """返回求职者所有的未读消息数"""
        unread_count_total = yield self.hr_chat_unread_count_ds.get_chat_unread_count_cnt(conds={
            "user_id": user_id,
        }, fields=["user_unread_count"])

        raise gen.Return(unread_count_total.count_user_unread_count)
