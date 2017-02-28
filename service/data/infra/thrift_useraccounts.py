# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.useraccounts.service.UserCenterService import Client as UsercenterServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class ThriftUseraccountsDataService(DataService):

    """对接 useraccounts 的 thrift 接口
    """

    usercenter_service_cilent = ServiceClientFactory.get_service(
        UsercenterServiceClient, CONF)

    @gen.coroutine
    def get_recommend_records(self, user_id, req_type, page_no, page_size):
        """
        推荐历史记录，调用 thrify 接口
        :param user_id:
        :param type: 数据类型 1表示浏览人数，2表示浏览人数中感兴趣的人数，3表示浏览人数中投递的人数
        :param page_no:
        :param page_size:
        :return:
        """
        self.logger.debug("[thrift]get_recommend_records user_id: {}".format(type(user_id)))
        self.logger.debug("[thrift]get_recommend_records type: {}".format(type(req_type)))
        self.logger.debug("[thrift]get_recommend_records page_no: {}".format(type(page_no)))
        self.logger.debug("[thrift]get_recommend_records page_size: {}".format(type(page_size)))
        ret = yield self.usercenter_service_cilent.getRecommendation(user_id, req_type, page_no, page_size)
        self.logger.debug("[thrift]get_recommend_records: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_fav_positions(self, user_id):
        """获得职位收藏，调用 thrify 接口"""

        ret = yield self.usercenter_service_cilent.getFavPositions(user_id)
        self.logger.debug("[thrift]get_fav_positions: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_applications(self, user_id):
        """获得求职记录，调用 thrify 接口"""

        ret = yield self.usercenter_service_cilent.getApplications(user_id)
        self.logger.debug("[thrift]get_applied_applications: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_applied_progress(self, app_id, user_id):
        """
        求职记录中的求职详情进度，调用 thrify 接口
        :param app_id:
        :param user_id:
        :return:
        """
        ret = yield self.usercenter_service_cilent.getApplicationDetail(app_id, user_id)
        self.logger.debug("[thrift]get_applied_progress: %s" % ret)
        raise gen.Return(ret)
