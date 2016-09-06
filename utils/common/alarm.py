# coding=utf-8

# @Time    : 9/6/16 15:12
# @Author  : tangyiliang (tangyiliang@moseeker.com）
# @File    : alarm.py
# @DES     : 第三方报警系统,已添加 salckman

# Copyright 2016 MoSeeker

import json
from utils.tool.http_tool import http_post
from setting import settings

# Moseeker Slack team webhook settings url:
# https://moseekermm.slack.com/services/B0TUGEK60#service_setup
SLACKMAN_WEBHOOK_URL="https://hooks.slack.com/services/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"


class Alarm(object):
    def __init__(self, webhook_url):
        self._webhook_url = webhook_url

    def biu(self, text, **kwargs):
        """
        slackman 报警
        :param text:
        :param kwargs:
        :return:
        """
        # debug 环境不报警
        assert text
        if not settings['debug']:
            payload = json.dumps({
                'text': text,
                'username': kwargs.get('botname'),
                'channel': kwargs.get('channel'),
                'icon_emoji': kwargs.get('emoji')
            })

            http_post(route=self._webhook_url, jdata=payload)

        return

Alarm = Alarm(SLACKMAN_WEBHOOK_URL)

if __name__ == '__main__':
    Alarm.biu('biu',
                 botname="脚小布",
                 channel="#wechat-error")
