# coding=utf-8


import collections
import itertools

import pypinyin
import tornado.gen as gen
from tornado.util import ObjectDict

import conf.common as const
import conf.path as path
from service.data.base import DataService
from util.common.decorator import cache
from util.tool.dict_tool import sub_dict
from util.tool.http_tool import http_get


class InfraDictDataService(DataService):
    cached_rocket_major = None
    cached_sms_country_codes = None

    # 热门城市编号列表
    _HOT_CITY_CODES_WECHAT = [
        110000, 310000, 330100, 440300, 440100, 510100,
        320100, 420100, 120000, 610100, 320500, 233333
    ]

    # 一级城市编号列表
    _LEVEL1_CITY_CODES = [
        110000, 120000, 310000, 500000, 810000, 820000
    ]

    # 港澳台城市编号前缀
    _GAT_PREFIX = [81, 82, 71]

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_const_dict(self, parent_code):
        """根据 parent_code 获取常量字典
        :param parent_code: 常量的 parent_code
        """

        if (parent_code is None or
            parent_code not in const.CONSTANT_PARENT_CODE.values()):
            raise ValueError('invalid parent_code')

        params = ObjectDict(parent_code=parent_code)
        response = yield http_get(path.DICT_CONSTANT, params)
        return self.make_const_dict_result(response, parent_code)

    @gen.coroutine
    def get_countries(self):
        """获取国家列表"""

        countries_res = yield http_get(path.DICT_COUNTRY)
        continent_res = yield self.get_const_dict(
            parent_code=const.CONSTANT_PARENT_CODE.CONTINENT)

        return self.make_countries_result(countries_res, continent_res)

    @gen.coroutine
    def get_sms_country_codes(self):
        """获取国家电话区号"""

        if self.cached_sms_country_codes:
            return self.cached_sms_country_codes

        countries_res = yield http_get(
            path.DICT_COUNTRY, jdata={'sms_enabled': 1})

        res = []
        for country in countries_res:
            to_append = ObjectDict()
            to_append.text = str(country['name'])
            to_append.text_code = str(country['code'])
            res.append(to_append)

        self.cached_sms_country_codes = res

        return res

    @staticmethod
    def make_countries_result(countries_res, continent_res):
        """获取国籍列表，按大洲分割 """

        filter_keys = ['id', 'name', 'continent_code']
        countries = countries_res.data

        def countries_gen(countries):
            for c in countries:
                d = sub_dict(c, filter_keys)
                d.code = d.id
                d.pop('id', None)
                yield d

        def filter_countries_gen(countries, continent):
            for c in countries:
                if c.continent_code == int(continent[0]):
                    c.pop('continent_code', None)
                    yield c

        res = []
        for continent in continent_res.items():
            res.append(
                ObjectDict(
                    text=continent[1],
                    list=list(filter_countries_gen(
                             list(countries_gen(countries)), continent))
            ))

        return res

    @staticmethod
    def make_const_dict_result(http_response, parent_code):
        """获取常量字典后的结果处理"""
        res_data = http_response.data
        ret = ObjectDict()
        for el in res_data.get(str(parent_code)):
            el = ObjectDict(el)
            setattr(ret, str(el.code), el.name)
        ret = collections.OrderedDict(sorted(ret.items()))
        return ret

    @staticmethod
    def make_college_list_result(http_response):
        res_data = http_response.data
        collegecode_list = []
        if isinstance(res_data, list):
            collegecode_nested_list = list(itertools.chain(
                map(lambda x: x.get("children", []), res_data)))
            for cn_list in collegecode_nested_list:
                for pair in cn_list:
                    collegecode_list.append(pair)
        return collegecode_list

    @gen.coroutine
    def get_college_code_by_name(self, school_name):
        """根据学校名称返回学校 code"""

        if school_name is None or not isinstance(school_name, str):
            raise ValueError('invalid school_name')
        colleges = yield self.get_colleges()
        return self.get_code_by_name_from(colleges, school_name)

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_colleges(self):
        """获取学校列表"""
        response = yield http_get(path.DICT_COLLEGE)
        return self.make_college_list_result(response)

    @staticmethod
    def get_code_by_name_from(colleges, school_name):
        ret = list(filter(lambda x: x.get('name') == school_name, colleges))
        if ret:
            code = ret[0].get('code', 0)
        else:
            code = 0
        return code

    @gen.coroutine
    def _get_level_1_cities(self):
        """获取一级城市列表"""
        params = dict(level=1, is_using=1)
        response = yield http_get(path.DICT_CITIES, params)
        return self._make_level_1_cities_result(response)

    def _make_level_1_cities_result(self, http_response):
        res_data = http_response.data
        return list(
            filter(lambda x: x.get('code') in self._LEVEL1_CITY_CODES,
                   res_data))

    @gen.coroutine
    def _get_level_2_cities(self):
        """获取二级城市列表"""
        params = dict(level=2, is_using=1)
        response = yield http_get(path.DICT_CITIES, params)
        return self._make_level_2_cities_result(response)

    @staticmethod
    def _make_level_2_cities_result(http_response):
        return http_response.data

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_cities(self, hot=False):
        """获取城市列表
        hot 为 True 为查询热门城市
        """
        level1_cities = yield self._get_level_1_cities()
        level2_cities = yield self._get_level_2_cities()

        return self.make_cities_result(level1_cities, level2_cities, hot)

    def make_cities_result(self, level1_cities, level2_cities, hot=False):
        """Merge level1/2 的城市数据，拼装并返回
        hot 为 True 为查询热门城市
        """
        res = level1_cities + level2_cities

        cities, ret, heads = [], [], []
        for e in res:
            ret.append(sub_dict(e, ['code', 'name']))

        if hot:
            cities = list(filter(
                lambda x: x.get('code') in self._HOT_CITY_CODES_WECHAT,
                ret))
            return cities

        else:
            from pypinyin import lazy_pinyin
            for el in ret:
                is_gat = any(
                    map(lambda x: str(el.get('code')).startswith(str(x)),
                        self._GAT_PREFIX))
                if is_gat:
                    h = "港,澳,台"
                else:
                    h = lazy_pinyin(
                        el.get('name'),
                        style=pypinyin.STYLE_FIRST_LETTER)[0].upper()

                if h not in heads:
                    cities_group = ObjectDict(text=h, list=[])
                    cities_group.list.append(ObjectDict(el))
                    cities.append(cities_group)
                    heads.append(h)
                else:
                    group = list(filter(lambda x: x.text == h, cities))[0]
                    group.list.append(el)

            ret = sorted(cities, key=lambda x: x.text)
            return ret

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_hot_cities(self):
        """Alias for get_cities(hot=False) :)"""
        cities = yield self.get_cities(hot=True)
        return cities

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_city_code_by(self, city_name):
        """city_name -> code
        :param city_name: city name, type: str
        :return: city code or 0 if city_name is not found
        """
        if city_name is None or not isinstance(city_name, str):
            raise ValueError('invalid city_name')

        http_response = yield self._get_level_2_cities()
        return self.make_city_code_by_name_result(http_response, city_name)

    @staticmethod
    def make_city_code_by_name_result(response, city_name):
        filtered = list(filter(lambda x: x.get('name') == city_name, response))
        if filtered:
            return filtered[0].get('code')
        else:
            return 0

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_city_name_by(self, city_code):
        """code -> city name
        :param city_code: type: int/str
        :return: None or city name
        """
        if city_code is None:
            raise ValueError('invalid city_code')
        try:
            city_code = int(city_code)
        except ValueError:
            raise ValueError('invalid city_code')

        http_response = yield self._get_level_2_cities()
        return self.make_city_name_by_code_result(http_response, city_code)

    @staticmethod
    def make_city_name_by_code_result(response, city_code):
        filtered = list(filter(lambda x: x.get('code') == city_code, response))
        if filtered:
            return filtered[0].get('name')
        else:
            return None

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_industries(self, level=2):
        """获取行业
        industries
        level1 + level2
        """
        ret = yield http_get(path.DICT_INDUSTRY, dict(parent=0))
        if level == 2:
            ret = yield self.make_industries_result(ret)
        return ret

    @staticmethod
    @gen.coroutine
    def make_industries_result(http_response):
        res_data = http_response.data
        industries = []
        for el in res_data:
            el = ObjectDict(el)
            out = ObjectDict()
            out.text = el.name
            level2 = yield http_get(path.DICT_INDUSTRY, dict(parent=el.code))
            out.list = list(map(lambda x: sub_dict(x, ['code', 'name']), level2.data))
            industries.append(out)
        return industries

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_functions(self, code=0):
        """获取职能
        Get functions (code=0 -> level1+level2, code!=0 -> level2+level3)
        """
        if not isinstance(code, int):
            raise ValueError('invalid code')

        http_response = yield http_get(path.DICT_POSITION, {})
        return self.get_function_result(http_response, code)

    def get_function_result(self, response, code=0):
        res_data = response.data
        if not code:
            # level1 and level2
            return self.get_function_result_level12(res_data)
        else:
            return self.get_function_result_level23(res_data, code)

    @staticmethod
    def get_function_result_level12(res_data):
        level1 = [ObjectDict(f) for f in res_data if f['level'] == 1]
        ret = []
        for l in level1:
            list = []
            level2 = [sub_dict(ObjectDict(f), ['code', 'name']) for f in res_data if f['parent'] == l.code and f['level'] == 2]
            for l2 in level2:
                list.append(l2)
            e = ObjectDict()
            e.list = list
            e.text = l.name
            ret.append(e)
        return ret

    @staticmethod
    def get_function_result_level23(res_data, code):
        level2 = [ObjectDict(f) for f in res_data if f['level'] == 2 and f['code'] == code][0]

        level3 = [sub_dict(ObjectDict(f), ['code', 'name']) for f in res_data
                  if f['parent'] == level2.code and f['level'] == 3]

        return level3

    @gen.coroutine
    def get_rocketmajors(self):

        if self.cached_rocket_major:
            return self.cached_rocket_major
        else:

            L1_res = yield http_get(path.DICT_CONSTANT,
                jdata=dict(parent_code=const.CONSTANT_PARENT_CODE.ROCKETMAJOR_L1))

            L1_res_data = L1_res.data.get(str(const.CONSTANT_PARENT_CODE.ROCKETMAJOR_L1))

            res = []

            for e in L1_res_data:
                e['text'] = e['name']
                e = sub_dict(e, ['code', 'text'])
                L2_res = yield http_get(path.DICT_CONSTANT,
                                        jdata=dict(parent_code=e['code']))
                L2_res_data = L2_res.data.get(str(e['code'])) #-> list
                L2_text_list = []
                for e2 in L2_res_data:
                    e2['text'] = e2['name']
                    e2 = sub_dict(e2, ['text'])
                    L2_text_list.append(e2)

                e['list'] = L2_text_list
                del e['code']
                res.append(e)


            self.cached_rocket_major = res
            return res
