# coding=utf-8

from service.page.base import PageService
from conf.common import *
import tornado.gen


class DictionaryPageService(PageService):

    @tornado.gen.coroutine
    def get_cities(self):
        ret = yield self.infra_dict_ds.get_cities()
        return ret

    @tornado.gen.coroutine
    def get_functions(self, code):
        ret = yield self.infra_dict_ds.get_functions(code)
        return ret

    @tornado.gen.coroutine
    def get_industries(self, level=2):
        ret = yield self.infra_dict_ds.get_industries(level=level)
        return ret

    @tornado.gen.coroutine
    def gen_mars_industries(self, level=2):
        ret = yield self.infra_dict_ds.get_mars_industries(level=level)
        return ret

    @tornado.gen.coroutine
    def get_constants(self, parent_code):
        ret = yield self.infra_dict_ds.get_const_dict(parent_code=parent_code)
        return ret

    @tornado.gen.coroutine
    def get_degrees(self, locale=None):
        ret = yield self.get_constants(parent_code=CONSTANT_PARENT_CODE.DEGREE_USER)
        if locale:
            ret_ = dict()
            for k in ret.keys():
                ret_[k] = locale.translate(HIGHEST_DEGREE.get(k))
            format_ret = [{'text': text, 'value': int(value)} for value, text in ret_.items()]
            format_ret_in_order = sorted(format_ret, key=lambda item: item['value'])
            return format_ret_in_order
        return ret

    @tornado.gen.coroutine
    def get_referral_relationship(self, locale=None):
        ret = yield self.get_constants(parent_code=CONSTANT_PARENT_CODE.REFERRAL_RELATIONSHIP)
        if locale:
            ret_ = dict()
            for k in ret.keys():
                ret_[k] = locale.translate(RELATIONSHIP.get(k))
            format_ret = [{'text': text, 'value': int(value)} for value, text in ret_.items()]
            format_ret_in_order = sorted(format_ret, key=lambda item: item['value'])
            returned_data = format_ret_in_order[1:]
            returned_data.append(format_ret_in_order[0])
            return returned_data
        return ret

    @tornado.gen.coroutine
    def get_colleges(self):
        ret = yield self.infra_dict_ds.get_colleges()
        return ret

    @tornado.gen.coroutine
    def get_mainland_colleges(self):
        ret = yield self.infra_dict_ds.get_mainland_colleges()
        return ret

    @tornado.gen.coroutine
    def get_overseas_colleges(self, country_id):
        ret = yield self.infra_dict_ds.get_overseas_colleges(country_id)
        return ret

    @tornado.gen.coroutine
    def get_countries(self, order):
        countries = yield self.infra_dict_ds.get_countries(order=order)
        return countries

    @tornado.gen.coroutine
    def get_rocketmajors(self):
        rocketmajors = yield self.infra_dict_ds.get_rocketmajors()
        return rocketmajors

    @tornado.gen.coroutine
    def get_sms_country_codes(self):

        ret = yield self.infra_dict_ds.get_sms_country_codes()

        china = {'text': '中国', 'code_text': '86'}

        try:
            ret.remove(china)
        except ValueError:
            pass

        finally:
            ret.insert(0, china)
            for item in [
                dict(code_text='852', text='中国香港'),
                dict(code_text='853', text='中国澳门'),
                dict(code_text='886', text='中国台湾'),
            ]:
                if item not in ret:
                    ret.append(item)
            return ret

    @tornado.gen.coroutine
    def get_sms_country_code_list(self):
        ret = yield self.infra_dict_ds.get_sms_country_code_list()
        return ret

    @tornado.gen.coroutine
    def get_industry_type_by_name(self, name):
        industry_raw_res = yield self.infra_dict_ds.get_industries_raw()

        if industry_raw_res.status == 0:
            for industry in industry_raw_res.data:
                if industry['name'] == name:
                    return industry['type']

        return 0

    @tornado.gen.coroutine
    def get_comment_tags_by_code(self, code):
        res = yield self.infra_dict_ds.get_comment_tags_by_code(code)
        return res
