# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.mq.service.MqService import Client as MqServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class ThriftMqDataService(DataService):

    """对接 mq 的 thrift 接口
    """

    mq_service_cilent = ServiceClientFactory.get_service(
        MqServiceClient, CONF)

    @gen.coroutine
    def send_sms(self, type, mobile, params):
        """
        发送短信，调用 thrift 接口
        :param type: int
        :param mobile: string
        :param params: dict
        :return:
        """

        ret = yield self.mq_service_cilent.sendSMS(type, str(mobile), params)
        self.logger.debug("[thrift]send_sms: %s" % ret)
        raise gen.Return(ret)


