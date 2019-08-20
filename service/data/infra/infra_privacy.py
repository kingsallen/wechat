# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, unboxing


class InfraPrivacyDataService(DataService):
    """隐私协议弹窗服务"""

    @gen.coroutine
    def if_privacy_agreement_window(self, user_id):
        """
        是否需要弹出“隐私协议”弹窗
        :param user_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id
        })
        ret = yield http_get(path.IF_PRIVACY_WINDOW, params)
        return unboxing(ret)

    @gen.coroutine
    def if_agree_privacy(self, user_id, status):
        """
        是否同意“隐私协议”
        :param user_id:
        :param status: 是否同意 1 同意， 0 不同意
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "status": status
        })
        ret = yield http_get(path.AGREE_PRIVACY, params)
        return ret

    @gen.coroutine
    def insert_privacy_record(self, user_id):
        """
        隐私协议需求：
        用户第一次在我们这里创建用户的时候 要插入一条记录
        :param user_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id
        })
        ret = yield http_get(path.INSERT_RECORD, params)
        return unboxing(ret)
