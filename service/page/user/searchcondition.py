# -*- coding:utf-8 -*-
from tornado import gen
from util.common import ObjectDict
from service.page.base import PageService


class SearchconditionPageService(PageService):

    @gen.coroutine
    def get_condition_list(self, userId):
        res = yield self.thrift_searchcondition_ds.userSearchConditionList(userId)
        res.searchConditionList=self.format_data(res.searchConditionList)
        raise gen.Return(res)

    def format_data(self, searchConditionList):
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
    def add_condition(self, userId=None, name=None, keywords=None,
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
    def del_condition(self, userId, id):
        res = yield self.thrift_searchcondition_ds.delUserSearchCondition(userId, id)
        raise gen.Return(res)

    @gen.coroutine
    def get_industries(self):
        res=yield self.dictionary_ps.get_industries()
        raise gen.Return(res)

    @gen.coroutine
    def get_city_list(self):
        res=yield self.dictionary_ps.get_city_list()
        raise gen.Return(res)
