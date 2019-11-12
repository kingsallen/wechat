# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.chat.service.ChatService import Client as ChatServiceClient
from util.tool.http_tool import http_get


class ThriftChatDataService(DataService):

    """对接 chat 的 thrift 接口
    referer: https://wiki.moseeker.com/chat-api.md
    """

    chat_service_cilent = ServiceClientFactory.get_service(
        ChatServiceClient)

    @gen.coroutine
    def chat_limit(self, params):
        """
        对聊天方式做限制
        """
        ret = yield http_get(path.CHAT_LIMIT, params)
        return ret

    @gen.coroutine
    def get_voice(self, params):
        """
        获取语音文件
        :param params:
        :return:
        """
        ret = yield http_get(path.VOICE, params)
        return ret
