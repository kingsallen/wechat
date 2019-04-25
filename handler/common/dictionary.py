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


class DictCustomIndustryHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self, source):
        try:
            # 重置 event，准确描述
            self._event = self._event + source
            yield getattr(self, 'get_' + source)()
        except Exception as e:
            self.send_json_error()

    @handle_response
    @gen.coroutine
    def get_mars(self):

        self.logger.debug("DictMarsIndustryHandler")

        mars_industries = yield self.dictionary_ps.gen_mars_industries()
        self.logger.debug("DictMarsIndustryHandler Mars_indurstries:{}".format(mars_industries))
        self.send_json_success(mars_industries)


class DictCountryHandler(BaseHandler):

    @handle_response
    @gen.coroutine
    def get(self):
        order = self.params.order
        countries = yield self.dictionary_ps.get_countries(order=order)
        self.send_json_success(countries)


class DictMainlandCollegeHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        colleges = yield self.dictionary_ps.get_mainland_colleges()
        self.send_json_success(colleges)


class DictOverseasCollegeHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        country_id = self.params.country_id
        colleges = yield self.dictionary_ps.get_overseas_colleges(country_id)
        self.send_json_success(colleges)


class DictHKMTCollegeHandler(BaseHandler):
    @handle_response
    @gen.coroutine
    def get(self):
        colleges = yield self.dictionary_ps.get_hkmt_colleges()
        self.send_json_success(colleges)


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
        display_locale = self.get_current_locale()
        sms_country_codes = yield self.dictionary_ps.get_sms_country_codes(display_locale)
        self.send_json_success(sms_country_codes)
