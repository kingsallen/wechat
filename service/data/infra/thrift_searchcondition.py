# -*- coding:utf-8 -*-

import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.searchcondition.service.searchservice.UserQxService import Client as SearchConditionServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory
from thrift_gen.gen.searchcondition.struct.usersearch.ttypes import UserSearchConditionDO


class ThriftSearchconditionDataService(DataService):
    searchcondition_service_cilent = ServiceClientFactory.get_service(
        SearchConditionServiceClient)

    @gen.coroutine
    def userSearchConditionList(self, userId):

        res = yield self.searchcondition_service_cilent.userSearchConditionList(userId)
        raise gen.Return(res)

    @gen.coroutine
    def postUserSearchCondition(self, userId=None, name=None, keywords=None,
                                cityName=None, salaryTop=None,
                                salaryBottom=None,
                                salaryNegotiable=None, industry=None):
        condition = UserSearchConditionDO(
            userId=userId,
            name=name,
            keywords=keywords,
            cityName=cityName,
            salaryTop=salaryTop,
            salaryBottom=salaryBottom,
            salaryNegotiable=salaryNegotiable,
            industry=industry)
        res = yield self.searchcondition_service_cilent.postUserSearchCondition(condition)
        raise gen.Return(res)

    @gen.coroutine
    def delUserSearchCondition(self, userId, id):
        res = yield self.searchcondition_service_cilent.delUserSearchCondition(userId, id)
        raise gen.Return(res)

    @gen.coroutine
    def get_user_position_status(self, user_id, position_ids):
        """
        批量查询用户职位状态
        :param user_id: int
        :param position_ids: list，如[110,112]
        :return:
        """

        ret = yield self.searchcondition_service_cilent.getUserPositionStatus(int(user_id), position_ids)
        self.logger.debug("[thrift]get_user_position_status: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def get_collect_position(self, user_id, position_id):
        """
        获取职位收藏状态
        :param user_id: int
        :param position_id: int
        :return:
        """

        ret = yield self.searchcondition_service_cilent.getUserCollectPosition(int(user_id), int(position_id))
        self.logger.debug("[thrift]get_collect_position: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def create_collect_position(self, user_id, position_id):
        """添加职位收藏，调用 thrift 接口"""

        ret = yield self.searchcondition_service_cilent.postUserCollectPosition(int(user_id), int(position_id))
        self.logger.debug("[thrift]create_collect_position: %s" % ret)
        raise gen.Return(ret)

    @gen.coroutine
    def delete_collect_position(self, user_id, position_id):
        """删除职位收藏，调用 thrift 接口"""

        ret = yield self.searchcondition_service_cilent.delUserCollectPosition(int(user_id), int(position_id))
        self.logger.debug("[thrift]delete_collect_position: %s" % ret)
        raise gen.Return(ret)
