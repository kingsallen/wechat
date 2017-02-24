# coding=utf-8

from tornado import gen
from service.page.base import PageService

from thrift_gen.gen.candidate.service.CandidateService import Client as CandidateServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from service.data.infra.framework.common.config import CONF


class CandidatePageService(PageService):

    candidate_service_cilent = ServiceClientFactory.get_service(
        CandidateServiceClient, "candidate", CONF)

    def __init__(self):
        super().__init__()


    @gen.coroutine
    def send_candidate_view_position(self, user_id, position_id, sharechain_id):
        """刷新候选人链路信息，调用基础服务"""

        ret = yield self.candidate_service_cilent.glancePosition(
            userId=user_id, positionId=position_id, shareChainId=sharechain_id)
        self.logger.debug("send_candidate_view_position: %s" % ret)
        raise gen.Return(ret)
