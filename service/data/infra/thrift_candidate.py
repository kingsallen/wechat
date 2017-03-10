# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.candidate.service.CandidateService import Client as CandidateServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class ThriftCandidateDataService(DataService):

    """对接 useraccounts 的 thrift 接口
    """

    candidate_service_cilent = ServiceClientFactory.get_service(
        CandidateServiceClient, CONF)

    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        ret = yield self.candidate_service_cilent.glancePosition(user_id, position_id, sharechain_id)
        self.logger.debug("[thrift]send_candidate_view_position: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def send_candidate_interested(self, user_id, position_id, is_interested):
        """刷新候选人感兴趣，调用基础服务"""

        ret = yield self.candidate_service_cilent.glancePosition(user_id, position_id, is_interested)
        self.logger.debug("[thrift]send_candidate_interested: %s" % ret)
        raise gen.Return(ret)
