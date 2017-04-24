# -*- coding:utf-8 -*-
from tornado.gen import coroutine, Return
from handler.base import BaseHandler
from conf.qx import hot_city
import json
from util.tool.http_tool import http_get
import conf.path as path

class SearchConditionHandler(BaseHandler):

    @coroutine
    def get(self):
        userid = self.current_user.sysuser.id
        res = yield self.searchcondition_ps.getConditionList(userid)

        conditionlist = res.searchConditionList
        if res.status == 0:
            self.send_json_success({'conditionlist': conditionlist})
        else:
            self.send_json_error(message=res.message)

    @coroutine
    def post(self):
        userId = self.current_user.sysuser.id
        condition = self.json_args

        name = condition.get('name', None)
        keywords = json.dumps(condition.get('keywords', None))
        if not (name and keywords and userId):
            self.send_json_error(message='Invalid argument')
        else:
            cityName = json.dumps(condition.get('cityName', None))
            salaryTop = condition.get('salaryTop', None)
            salaryBottom = condition.get('salaryBottom', None)
            salaryNegotiable = condition.get('salaryNegotiable', None)
            industry = json.dumps(condition.get('industry', None))

            res = yield self.searchcondition_ps.addCondition(userId=userId, name=name, keywords=keywords,
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
        res = yield self.searchcondition_ps.delCondition(int(userId), int(id))
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
        res = hot_city
        raise Return(res)

    @coroutine
    def get_city_list(self):
        res = yield self.dictionary_ps.get_cities()
        raise Return(res)

    @coroutine
    def get_industries(self):
        response = yield http_get(path.DICT_INDUSTRY, dict(parent=0))
        industries_list=response.data
        res = map(lambda x: x['name'], industries_list)
        raise Return({"industries": list(res)})



