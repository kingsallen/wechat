# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.position.service.PositionServices import Client as PositionServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory


class ThriftPositionDataService(DataService):

    """对接 position 的 thrift 接口
    referer: https://wiki.moseeker.com/position-api.md
    """

    position_service_cilent = ServiceClientFactory.get_service(
        PositionServiceClient)

    @gen.coroutine
    def get_aggregation_banner(self):
        """
        查找聚合号列表运营头图，调用 thrift 接口
        :return:
        """

        ret = yield self.position_service_cilent.headImage()
        self.logger.debug("[thrift]get_aggregation_banner: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_company_positions(self, company_id, page_no, page_size):
        """
        查找聚合号企业热招职位，调用 thrift 接口
        :return:
        """

        self.logger.debug("[thrift]get_aggregation_banner company_id: %s" % company_id)
        self.logger.debug("[thrift]get_aggregation_banner page_no: %s" % page_no)
        self.logger.debug("[thrift]get_aggregation_banner page_size: %s" % page_size)
        ret = yield self.position_service_cilent.companyHotPositionDetailsList(int(company_id), int(page_no), int(page_size))
        self.logger.debug("[thrift]get_company_positions: %s" % ret)
        raise gen.Return(ret)
