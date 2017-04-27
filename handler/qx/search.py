# -*- coding:utf-8 -*-
from tornado.gen import coroutine, Return
from handler.base import BaseHandler
from conf.qx import HOTCITY
from util.tool.json_tool import json_dumps


class SearchConditionHandler(BaseHandler):

    @coroutine
    def get(self):
        userid = self.current_user.sysuser.id
        res = yield self.searchcondition_ps.get_condition_list(userid)

        conditionlist = res.searchConditionList
        if res.status == 0:
            self.send_json_success({'conditionlist': conditionlist})
        else:
            self.send_json_error(message=res.message)

    @coroutine
    def post(self):
        userId = self.current_user.sysuser.id or 1
        condition = self.json_args

        name = condition.get('name', None)
        keywords = condition.get('keywords', None)
        if not (name and keywords and userId):
            self.send_json_error(message='Invalid argument')
        else:
            cityNameData = condition.get('cityName', None)
            industryData = condition.get('industry', None)
            cityName = json_dumps(cityNameData ) if cityNameData else None
            industry = json_dumps(industryData ) if industryData else None

            salaryTop = condition.get('salaryTop', None)
            salaryBottom = condition.get('salaryBottom', None)
            salaryNegotiable = condition.get('salaryNegotiable', None)

            res = yield self.searchcondition_ps.add_condition(userId=userId, name=name, keywords=json_dumps(keywords),
                                                             cityName=cityName, salaryTop=salaryTop,
                                                             salaryBottom=salaryBottom,
                                                             salaryNegotiable=salaryNegotiable, industry=industry)

            if res.status == 0:
                self.send_json_success()
            else:
                self.send_json_error(message=res.message)

    @coroutine
    def delete(self, id):
        userId = self.current_user.sysuser.id
        res = yield self.searchcondition_ps.del_condition(int(userId), int(id))
        if res.status == 0:
            self.send_json_success()
        else:
            self.send_json_error(message=res.message)


class SearchCityHandler(BaseHandler):

    @coroutine
    def get(self, action=''):
        func = getattr(self, 'get_' + action, None)
        if not func:
            self.send_json_error(message='Invalid cities params')
        else:
            res = yield func()
            self.send_json_success(res)

    @coroutine
    def get_hot_city(self):
        res = HOTCITY
        raise Return(res)

    @coroutine
    def get_city_list(self):
        res=yield self.dictionary_ps.get_city_list()
        raise Return(res)

    @coroutine
    def get_industries(self):
        response = yield self.dictionary_ps.get_industries(level=1)
        industries_list=response.data
        res = map(lambda x: x['name'], industries_list)
        raise Return({"industries": list(res)})

