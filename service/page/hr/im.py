# coding=utf-8

# @Time    : 10/27/16 14:42
# @Author  : panda (panyuxin@moseeker.com)
# @File    : im.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService


class ImPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_chats(self, conds, fields=None, options=None, appends=None):
        """返回聊天内容"""

        fields = fields or []
        options = options or []
        appends = appends or []

        ret = yield self.hr_wx_hr_chat_ds.get_chats(conds, fields, options, appends)
        raise gen.Return(ret)

    @gen.coroutine
    def get_chatroom(self, conds):
        """返回单个聊天室"""

        ret = yield self.hr_wx_hr_chat_list_ds.get_chatroom(conds)
        raise gen.Return(ret)

    @gen.coroutine
    def get_unread_chat_num(self, user_id, hr_id):

        """返回JD 页，求职者与 HR 之间的未读消息数"""
        chatroom = yield self.hr_wx_hr_chat_list_ds.get_chatroom(conds={
            "sysuser_id": user_id,
            "hraccount_id": hr_id
        })

        # 若无聊天，则默认显示1条未读消息
        if not chatroom:
            raise gen.Return(1)

        # 查看 HR 的留言
        chats = yield self.hr_wx_hr_chat_ds.get_chats(
            conds={
                "chatlist_id": chatroom.id,
                "speaker": 1,
                "status": 0,
            }
        )

        chat_num = 0
        if not chatroom.wx_chat_time:
            chat_num = len(chats)
        else:
            for chat in chats:
                if chatroom.wx_chat_time < chat.create_time:
                    chat_num += 1

        raise gen.Return(chat_num)

    @gen.coroutine
    def get_all_unread_chat_num(self, user_id):

        """返回求职者所有的未读消息数，供侧边栏我的消息未读消息提示"""

        chatrooms = yield self.hr_wx_hr_chat_list_ds.get_chatroom_list(conds={
            "sysuser_id": user_id
        })

        chat_num = 0

        for chatroom in chatrooms:
            # 查看 HR 的留言
            chats = yield self.hr_wx_hr_chat_ds.get_chats(
                conds={
                    "chatlist_id": chatroom.id,
                    "speaker": 1,
                    "status": 0,
                }
            )

            if not chatroom.wx_chat_time:
                chat_num += len(chats)
            else:
                for chat in chats:
                    if chatroom.wx_chat_time < chat.create_time:
                        chat_num += 1

        raise gen.Return(chat_num)
