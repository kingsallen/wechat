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
    def userSearchConditionList(self,userId):
        res=yield self.searchcondition_service_cilent.userSearchConditionList(userId)
        raise gen.Return(res)

    @gen.coroutine
    def postUserSearchCondition(self,condition):
        condition=UserSearchConditionDO(name='test',keywords='["java", "php"]',userId=1)
        res=yield self.searchcondition_service_cilent.postUserSearchCondition(condition)
        raise gen.Return(res)




