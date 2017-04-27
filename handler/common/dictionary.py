# coding=utf-8

import tornado.gen as gen

from handler.base import BaseHandler
from util.common.decorator import handle_response


class DictCityHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        cities = yield self.dictionary_ps.get_cities()
        self.send_json_success(cities)


class DictFunctionHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        functions = yield self.dictionary_ps.get_functions(
            code=int(self.params.fcode) if self.params.fcode else 0)
        self.send_json_success(functions)


class DictIndustryHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        industries = yield self.dictionary_ps.get_industries()
        self.send_json_success(industries)
