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
        self.logger.debug("DictIndustryHandler")

        industries = yield self.dictionary_ps.get_industries()
        self.logger.debug("DictIndustryHandler indurstries:{}".format(industries))
        self.send_json_success(industries)


class DictCountryHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        countries = yield self.dictionary_ps.get_counries()
        self.send_json_success(countries)


class DictRocketMajorHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        rocketmajors = yield self.dictionary_ps.get_rocketmajors()
        self.send_json_success(rocketmajors)


class DictSmsCountryCodeHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        sms_country_codes = yield self.dictionary_ps.get_sms_country_codes()
        self.send_json_success(sms_country_codes)
