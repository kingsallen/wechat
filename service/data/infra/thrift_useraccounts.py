# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.useraccounts.service.UserCenterService import Client as UsercenterServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory


class ThriftUseraccountsDataService(DataService):

    """对接 useraccounts 的 thrift 接口
    """

    usercenter_service_cilent = ServiceClientFactory.get_service(
        UsercenterServiceClient)

    @gen.coroutine
    def get_recommend_records(self, user_id, req_type, page_no, page_size):
        """
        推荐历史记录，调用 thrift 接口
        :param user_id:
        :param req_type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        ret = yield self.usercenter_service_cilent.getRecommendation(user_id, req_type, page_no, page_size)
        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_progress(self, user_id, app_id):
        """
        求职记录中的求职详情进度，调用 thrift 接口
        :param app_id:
        :param user_id:
        :return:
        """

        ret = yield self.usercenter_service_cilent.getApplicationDetail(user_id, int(app_id))
        raise gen.Return(ret)
