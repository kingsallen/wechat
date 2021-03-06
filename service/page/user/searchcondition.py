# -*- coding:utf-8 -*-

from tornado import gen
from util.common import ObjectDict
from service.page.base import PageService
import json

class SearchconditionPageService(PageService):

    @gen.coroutine
    def get_condition_list(self, user_id):

        res = yield self.thrift_searchcondition_ds.userSearchConditionList(user_id)
        conditionlist=self.format_data(res.searchConditionList)
        raise gen.Return(conditionlist)

    def format_data(self, search_condition_list):

        data = []
        for i in search_condition_list:
            data.append({
                'id': i.id,
                'name': i.name,
                'keywords': json.loads(i.keywords) if i.keywords else [],
                'city_name': json.loads(i.cityName) if i.cityName else [],
                'salary_top': i.salaryTop,
                'salary_bottom': i.salaryBottom,
                'salary_negotiable': i.salaryNegotiable,
                'industry': json.loads(i.industry) if i.industry else [],
                'sysuser_id': i.userId,
                'disable': i.disable,
                'create_time': i.createTime,
            })
        return data

    @gen.coroutine
    def add_condition(self, user_id=None, name=None, keywords=None,
                     city_name=None, salary_top=None,
                     salary_bottom=None,
                     salary_negotiable=None, industry=None):

        res = yield self.thrift_searchcondition_ds.postUserSearchCondition(userId=user_id, name=name,
                                                                           keywords=keywords,
                                                                           cityName=city_name, salaryTop=salary_top,
                                                                           salaryBottom=salary_bottom,
                                                                           salaryNegotiable=salary_negotiable,
                                                                           industry=industry)
        raise gen.Return(res)

    @gen.coroutine
    def del_condition(self, user_id, id):

        res = yield self.thrift_searchcondition_ds.delUserSearchCondition(int(user_id), int(id))
        raise gen.Return(res)

    @gen.coroutine
    def get_industries(self, level):

        res = yield self.infra_dict_ds.get_industries(level=level)
        industries_list = res.data
        res = map(lambda x: x['name'], industries_list)
        return res

    @gen.coroutine
    def get_city_list(self):

        res = yield self.infra_dict_ds.get_city_list()
        raise gen.Return(res)
