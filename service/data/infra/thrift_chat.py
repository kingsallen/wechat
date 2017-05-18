# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.chat.service.ChatService import Client as ChatServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory


class ThriftChatDataService(DataService):

    """对接 chat 的 thrift 接口
    referer: https://wiki.moseeker.com/chat-api.md
    """

    chat_service_cilent = ServiceClientFactory.get_service(
        ChatServiceClient)

    @gen.coroutine
    def get_chatrooms_list(self, user_id, page_no, page_size):
        """
        用户查找聊天室列表，调用 thrift 接口
        :param user_id:
        :param page_no:
        :param page_size:
        :return:
        """

        ret = yield self.chat_service_cilent.listUserChatRoom(int(user_id), int(page_no), int(page_size))
        self.logger.debug("[thrift]get_chatrooms_list: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_chats(self, room_id, page_no, page_size):
        """
        用户查找聊天记录列表，调用 thrift 接口
        :param room_id:
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.chat_service_cilent.listChatLogs(int(room_id), int(page_no), int(page_size))
        self.logger.debug("[thrift]get_chats: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def enter_chatroom(self, user_id, hr_id, position_id, room_id, is_gamma=False):
        """
        进入聊天室，调用 thrift 接口
        :param user_id:
        :param hr_id:
        :param position_id:
        :param room_id
        :param is_gamma: 是否为 gamma，欢迎语不同
        :return:
        """

        ret = yield self.chat_service_cilent.enterRoom(int(user_id), int(hr_id), int(position_id), int(room_id), is_gamma)
        self.logger.debug("[thrift]enter_chatroom: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def leave_chatroom(self, room_id, speaker):
        """
        离开聊天室，调用 thrift 接口
        :param room_id:
        :param speaker: 0：求职者，1：HR
        :return:
        """

        ret = yield self.chat_service_cilent.leaveChatRoom(int(room_id), int(speaker))
        self.logger.debug("[thrift]leave_chatroom: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def save_chat(self, room_id, content, position_id, speaker):
        """
        记录聊天内容
        :param room_id:
        :param content:
        :param position_id:
        :param speaker: 0：求职者，1：HR
        :return:
        """

        self.logger.debug("save_chat start")
        self.logger.debug("[save_chat]room_id:{}".format(int(room_id)))
        self.logger.debug("[save_chat]content:{}".format(str(content)))
        self.logger.debug("[save_chat]position_id:{}".format(position_id))
        self.logger.debug("[save_chat]speaker:{}".format(speaker))
        self.logger.debug("save_chat end")

        ret = yield self.chat_service_cilent.saveChat(int(room_id), str(content), int(position_id), int(speaker))
        self.logger.debug("[thrift]save_chat: %s" % ret)
        raise gen.Return(ret)
