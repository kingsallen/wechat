# coding=utf-8

import tornado.gen as gen

from tornado.escape import json_encode
from handler.base import BaseHandler
from util.common.decorator import handle_response


class DictCityHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        cities = yield self.dictionary_ps.get_cities()
        self.send_json_success(json_encode(cities))


class DictFunctionHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        self.guarantee('code')
        functions = yield self.dictionary_ps.get_functions(
            code=int(self.params.code) if self.params.code else 0)
        self.send_json_success(json_encode(functions))


class DictIndustryHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        industries = yield self.dictionary_ps.get_industries()
        self.send_json_success(json_encode(industries))
