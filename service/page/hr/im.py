# coding=utf-8

# @Time    : 10/27/16 14:42
# @Author  : panda (panyuxin@moseeker.com)
# @File    : im.py
# @DES     :

# Copyright 2016 MoSeeker

from tornado import gen
from service.page.base import PageService


class ImPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

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
    def get_chatroom_list(self, conds, fields, options=None, appends=None):
        """返回返回聊天室列表"""

        options = options or []
        appends = appends or []

        ret = yield self.hr_wx_hr_chat_list_ds.get_chatroom_list(conds, fields, options, appends)
        raise gen.Return(ret)

    @gen.coroutine
    def get_unread_chat_num(self, user_id, hr_id):

        """返回JD 页，求职者与 HR 之间的未读消息数"""
        chatroom = yield self.hr_wx_hr_chat_list_ds.get_chatroom(conds={
            "sysuser_id": user_id,
            "hraccount_id": hr_id
        })

        append = " AND (`hr_chat_time` is null OR `hr_chat_time` < {})".format(chatroom.create_time)
        chat_num = yield self.hr_wx_hr_chat_ds.get_chats_num(
            conds={
                "chatlist_id": chatroom.id,
                "speaker": 0,
                "status": 0,
            },
            fields=["id"],
            appends=[append]
        )

        raise gen.Return(chat_num)


