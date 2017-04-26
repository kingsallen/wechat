# -*- coding:utf-8 -*-
from tornado import gen
from util.common import ObjectDict
from service.page.base import PageService


class SearchconditionPageService(PageService):

    @gen.coroutine
    def getConditionList(self, userId):
        res = yield self.thrift_searchcondition_ds.userSearchConditionList(userId)
        res.searchConditionList=self.formatData(res.searchConditionList)
        raise gen.Return(res)

    def formatData(self, searchConditionList):
        data = []
        for i in searchConditionList:
            data.append({
                'id': i.id,
                'name': i.name,
                'keywords': i.keywords,
                'cityName': i.cityName,
                'salaryTop': i.salaryTop,
                'salaryBottom': i.salaryBottom,
                'salaryNegotiable': i.salaryNegotiable,
                'industry': i.industry,
                'userId': i.userId,
                'disable': i.disable,
                'createTime': i.createTime,
            })
        return data

    @gen.coroutine
    def addCondition(self, userId=None, name=None, keywords=None,
                     cityName=None, salaryTop=None,
                     salaryBottom=None,
                     salaryNegotiable=None, industry=None):

        res = yield self.thrift_searchcondition_ds.postUserSearchCondition(userId=userId, name=name,
                                                                           keywords=keywords,
                                                                           cityName=cityName, salaryTop=salaryTop,
                                                                           salaryBottom=salaryBottom,
                                                                           salaryNegotiable=salaryNegotiable,
                                                                           industry=industry)
        raise gen.Return(res)

    @gen.coroutine
    def delCondition(self, userId, id):
        res = yield self.thrift_searchcondition_ds.delUserSearchCondition(userId, id)
        raise gen.Return(res)
