# -*- coding:utf-8 -*-

from tornado.gen import coroutine,Return
from handler.base import BaseHandler
from conf.qx import hot_city
from util.common.decorator import authenticated,handle_response
from util.tool.http_tool import http_post,http_delete,http_get
import conf.path as path
# from service.data.infra.thrift_searchcondition import ThriftSearchconditionDataService
class SearchConditionHandler(BaseHandler):

    @coroutine
    def get(self):
        userid=self.current_user.sysuser.id
        res=yield self.searchcondition_ps.getConditionList(userid)
        conditionlist=res.searchConditionList
        self.send_json_success({'searchs':conditionlist})


    @coroutine
    def post(self):

        userid=self.current_user.sysuser.id

        condition = self.json_args.data

        condition['userId']=userid or 1
        print('condition is',condition)
        res = yield self.searchcondition_ps.addCondition(condition)
        print(res)
        print('@@@@######')
        # if res.status==0:
        #     self.send_json_success()
        # else:
        #     self.send_json_error(message = res.message)

    @coroutine
    def delete(self,id):
        userid=self.current_user.sysuser.id

        jdata={
            "userid":userid,
            "id": id
        }
        res=yield http_delete(path.SEARCH_CONDITION,jdata,infra = True)
        self.send_json_success(res)

# class SearchConditionHandler(BaseHandler):
#
#     @coroutine
#     def get(self):
#         userid=self.current_user.sysuser.id
#
#         res = yield http_get(path.SEARCH_CONDITION, {'sysuser_id':userid}, infra = True)
#         self.send_json_success(res)
#
#     @coroutine
#     def post(self):
#
#         userid=self.current_user.sysuser.id
#
#         condition = self.json_args.data
#         condition['sysuser_id']=userid
#
#         res = yield http_post(path.SEARCH_CONDITION, condition, infra = True)
#         self.send_json_success(res)
#
#     @coroutine
#     def delete(self,id):
#         userid=self.current_user.sysuser.id
#
#         jdata={
#             "userid":userid,
#             "id": id
#         }
#         res=yield http_delete(path.SEARCH_CONDITION,jdata,infra = True)
#         self.send_json_success(res)



class SearchCityHandler(BaseHandler):
    @coroutine
    def get(self,action=''):
        func=getattr(self,'get_'+action,None)
        if not func:
            self.send_json_error(message = 'Invalid cities params')
        else:
            res=yield func()
            self.send_json_success(res)

    @coroutine
    def get_hot_city(self):
        res=hot_city
        raise Return(res)

    @coroutine
    def get_city_list(self):
        res=yield self.dictionary_ps.get_cities()
        raise Return(res)

    @coroutine
    def get_industries(self):

        industries_list = yield self.dictionary_ps.get_industries()
        res=map(lambda x:x['text'],industries_list)

        raise Return({"industries":list(res)})
