# -*- coding:utf-8 -*-

from tornado.gen import coroutine,Return
from handler.base import BaseHandler
from conf.qx import hot_city
from util.common.decorator import authenticated,handle_response
from util.tool.http_tool import http_post,http_delete,http_get
import conf.path as path


import tornado.gen as gen

from service.data.base import DataService
from util.common import ObjectDict
from util.common.decorator import cache
from thrift_gen.gen.searchcondition.service.searchservice.UserQxService import Client as ChatServiceClient
from service.data.infra.framework.client.client import ServiceClientFactory


class test(DataService):

    chat_service_cilent = ServiceClientFactory.get_service(
        ChatServiceClient)

    @gen.coroutine
    def get(self):
        res=yield self.userSearchConditionList(1)
        print(res)
        print('-------------')

    @gen.coroutine
    def userSearchConditionList(self, user_id):

        ret = yield self.chat_service_cilent.userSearchConditionList(int(user_id))

        raise gen.Return(ret)



class SearchConditionHandler(BaseHandler):

    @coroutine
    def get(self):
        userid=self.current_user.sysuser.id

        res = yield http_get(path.SEARCH_CONDITION, {'sysuser_id':userid}, infra = True)
        self.send_json_success(res)

    @coroutine
    def post(self):

        userid=self.current_user.sysuser.id

        condition = self.json_args.data
        condition['sysuser_id']=userid

        res = yield http_post(path.SEARCH_CONDITION, condition, infra = True)
        self.send_json_success(res)

    @coroutine
    def delete(self,id):
        userid=self.current_user.sysuser.id

        jdata={
            "userid":userid,
            "id": id
        }
        res=yield http_delete(path.SEARCH_CONDITION,jdata,infra = True)
        self.send_json_success(res)



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
