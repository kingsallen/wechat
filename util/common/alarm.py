# coding=utf-8

# @Time    : 9/6/16 15:12
# @Author  : tangyiliang (tangyiliang@moseeker.com）
# @File    : alarm.py
# @DES     : 第三方报警系统,已添加 salckman

# Copyright 2016 MoSeeker
from tornado import gen

import socket
import json
from util.tool.http_tool import http_post
from setting import settings

# Moseeker Slack team webhook settings url:
# https://moseekermm.slack.com/services/B0TUGEK60#service_setup
SLACKMAN_WEBHOOK_URL="https://hooks.slack.com/services/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"


class Alarm(object):
    def __init__(self):
        self._webhook_url = SLACKMAN_WEBHOOK_URL

    @gen.coroutine
    def biu(self, text, **kwargs):
        """
        slackman 报警
        :param text:
        :param kwargs:
        :return:
        """
        # debug 环境不报警
        assert text
        text = "[{0}]: {1}".format(socket.gethostname(), text)
        payload = {
            'text': text,
            'username': kwargs.get('botname') or "NEW-WECHAT",
            'channel': kwargs.get('channel') or "#script-alert", # wechat-error
            'icon_emoji': kwargs.get('emoji')
        }

        # TODO 待调试

        yield http_post(route=self._webhook_url, jdata=payload)

        return

if __name__ == '__main__':
    try:
        alarm = Alarm()
        alarm.biu('biu')
    except Exception as e:
        print (e)
