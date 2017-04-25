# coding=utf-8

# import tornado.gen as gen
#
from service.data.base import DataService
# from util.common import ObjectDict
# from util.common.decorator import cache
# from thrift_gen.gen.chat.service.ChatService import Client as ChatServiceClient
# from service.data.infra.framework.client.client import ServiceClientFactory
#
#
class ThriftPositionDataService(DataService):

    pass
#
#     """对接 position 的 thrift 接口
#     referer: https://wiki.moseeker.com/position-api.md
#     """
#
#     position_service_cilent = ServiceClientFactory.get_service(
#         PositionServiceClient)
#
#     @gen.coroutine
#     def get_aggregation_banner(self):
#         """
#         查找聚合号列表运营头图，调用 thrift 接口
#         :return:
#         """
#
#         ret = yield self.position_service_cilent.getAggregationBanner()
#         self.logger.debug("[thrift]get_aggregation_banner: %s" % ret)
#         raise gen.Return(ret)
