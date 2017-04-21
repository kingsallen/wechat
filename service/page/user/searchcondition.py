# -*- coding:utf-8 -*-
from tornado import gen

from service.page.base import PageService

class SearchconditionPageService(PageService):
    @gen.coroutine
    def getConditionList(self,userId):
        res=yield self.thrift_searchcondition_ds.userSearchConditionList(userId)
        raise gen.Return(res)

    @gen.coroutine
    def addCondition(self, condition):
        res = yield self.thrift_searchcondition_ds.postUserSearchCondition(condition)
        raise gen.Return(res)
