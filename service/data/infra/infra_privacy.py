# coding=utf-8

import tornado.gen as gen

import conf.path as path
from service.data.base import DataService
from util.common import ObjectDict
from util.tool.http_tool import http_get, unboxing, http_get_v2, http_post_v2
from conf.newinfra_service_conf.service_info import user_service
from conf.newinfra_service_conf.user import user
import conf.common as const
from util.common.exception import InfraOperationError


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

    @gen.coroutine
    def if_custom_privacy_window(self, user_id, company_id):
        """
        是否需要弹出“客户自定义隐私协议”弹窗: 获取用户确认状态
        :param user_id, company_id:
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id
        })
        ret = yield http_get_v2(user.INFRA_IF_CUSTOM_PRIVACY_WINDOW, user_service, params)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        return ret


    @gen.coroutine
    def get_custom_privacy_info(self, company_id):
        """
        获取客户自定义隐私协议信息
        :param company_id:
        :return:
        """
        params = ObjectDict({
            "company_id": company_id
        })
        ret = yield http_get_v2(user.INFRA_GET_CUSTOM_PRIVACY_INFO, user_service, params)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        return ret


    @gen.coroutine
    def if_agree_custom_privacy(self, user_id, company_id):
        """
        是否同意“客户自定义隐私协议”
        :param user_id:
        :param status: 是否同意 1 同意， 0 不同意
        :return:
        """
        params = ObjectDict({
            "user_id": user_id,
            "company_id": company_id
        })
        ret = yield http_post_v2(user.INFRA_IF_AGREE_CUSTOM_PRIVACY, user_service, params)
        if ret.code != const.NEWINFRA_API_SUCCESS:
            raise InfraOperationError(ret.message)
        return ret
