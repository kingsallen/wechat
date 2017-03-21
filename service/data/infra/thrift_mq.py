# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.mq.service.MqService import Client as MqServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF
from util.tool.json_tool import json_dumps


class ThriftMqDataService(DataService):

    """对接 mq 的 thrift 接口
    """

    mq_service_cilent = ServiceClientFactory.get_service(
        MqServiceClient, CONF)

    @gen.coroutine
    def send_sms(self, sms_type, mobile, params, sys, ip):
        """
        发送短信，调用 thrift 接口
        :param sms_type: int
        :param mobile: string
        :param params: dict
        :return:
        """

        ret = yield self.mq_service_cilent.sendSMS(sms_type, str(mobile), params, str(sys), str(ip))
        self.logger.debug("[thrift]send_sms: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def send_mandrill_email(self, template_name, to_email, subject, from_email, from_name, to_name, merge_vars):
        """
        发送 mandrill 邮件
        :param template_name: string 必填 mandrill模板名称,eg mars-failed-to-apply-for-job
        :param to_email: string 必填 收件人邮件地址
        :param subject: string  选填 邮件主题, 一般不填, 使用模板设定的主题
        :param from_email: string 选填 发件人邮箱, 一般不填, 使用模板设定的默认值
        :param from_name: string 选填 发件人名称, 一般不填, 使用模板设定的默认值
        :param to_name: string 选填 暂不生效, 使用email中的@前面的用户名作为收件人名称
        :param merge_vars: dict 选填 形如 {"name":"张三","position_title":"java engineer","send_time":"2016-11-28"}, 不同的模板, 定义的变量不一致.
        :return:
        """

        params = {
            "templateName" : str(template_name),
            "to_email": str(to_email),
            "mergeVars": json_dumps(merge_vars),
            "subject": subject,
            "from_email": from_email,
            "from_name": from_name,
            "to_name": to_name
        }

        ret = yield self.mq_service_cilent.sendMandrilEmail(params)
        self.logger.debug("[thrift]send_mandrill_email: %s" % ret)
        raise gen.Return(ret)
