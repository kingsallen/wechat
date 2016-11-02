# coding=utf-8

# @Time    : 9/6/16 15:12
# @Author  : tangyiliang (tangyiliang@moseeker.com）
# @File    : alarm.py
# @DES     : 第三方报警系统,已添加 salckman

# Copyright 2016 MoSeeker

import requests
import ujson
import socket

# Moseeker Slack team webhook settings url:
# https://moseekermm.slack.com/services/B0TUGEK60#service_setup
WEBHOOK_URL="https://hooks.slack.com/services/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"


class Alarm(object):
    def __init__(self, webhook_url):
        self._webhook_url = webhook_url

    def biu(self, text, **kwargs):
        assert text
        text = "[{0}]: {1}".format(socket.gethostname(), text)
        payload = ujson.dumps({
            'text': text,
            'username': "new_wechat",
            'channel': kwargs.get('channel') or "#wechat-error",
            'icon_emoji': kwargs.get('emoji')
        })

        ret = requests.post(self._webhook_url, data=payload)
        return ret.content == 'ok'

Alarm = Alarm(WEBHOOK_URL)

if __name__ == '__main__':
    Alarm.biu('biu')
