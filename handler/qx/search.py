# -*- coding:utf-8 -*-

from tornado.gen import coroutine

import conf.qx as qx_const

from handler.base import BaseHandler
from util.common.decorator import handle_response, authenticated
from util.tool.json_tool import json_dumps


class SearchConditionHandler(BaseHandler):

    @handle_response
    @authenticated
    @coroutine
    def get(self):

        res = yield self.searchcondition_ps.get_condition_list(self.current_user.sysuser.id)
        self.send_json_success({'conditionlist': res[:3]})

    @handle_response
    @authenticated
    @coroutine
    def post(self):

        condition = self.json_args

        name = condition.get('name', None)
        keywords = condition.get('keywords', None)
        conditions = yield self.searchcondition_ps.get_condition_list(self.current_user.sysuser.id)
        if len(conditions)>=3:
            pass
        elif not (name and keywords and self.current_user.sysuser.id):
            self.send_json_error(message='Invalid argument')
        else:
            cityNameData = condition.get('city_name', None)
            industryData = condition.get('industry', None)
            cityName = json_dumps(cityNameData) if cityNameData else None
            industry = json_dumps(industryData) if industryData else None

            salary_top = condition.get('salary_top', None)
            salary_bottom = condition.get('salary_bottom', None)
            salary_negotiable = condition.get('salary_negotiable', None)

            res = yield self.searchcondition_ps.add_condition(user_id=self.current_user.sysuser.id,
                                                              name=name,
                                                              keywords=json_dumps(keywords),
                                                              city_name=cityName,
                                                              salary_top=salary_top,
                                                              salary_bottom=salary_bottom,
                                                              salary_negotiable=salary_negotiable,
                                                              industry=industry)

            if res.status == 0:
                self.send_json_success()
            else:
                self.send_json_error(message=res.message)

    @handle_response
    @authenticated
    @coroutine
    def delete(self, id):

        res = yield self.searchcondition_ps.del_condition(self.current_user.sysuser.id, id)
        if res.status == 0:
            self.send_json_success()
        else:
            self.send_json_error(message=res.message)


class SearchCityHandler(BaseHandler):

    @handle_response
    @coroutine
    def get(self, action=''):
        func = getattr(self, 'get_' + action, None)
        self._event = self._event + action
        if not func:
            self.send_json_error(message='Invalid cities params')
        else:
            yield func()

    @handle_response
    @coroutine
    def get_hot_city(self):

        self.send_json_success(data={
            "hot_city": qx_const.HOTCITY
        })

    @handle_response
    @coroutine
    def get_industries(self):


        self.send_json_success(data={
            "industries": qx_const.INDUSTRIES
        })
