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
from util.tool.dict_tool import sub_dict, rename_keys
from util.tool.http_tool import http_get, unboxing, http_get_v2
from pypinyin import lazy_pinyin
from conf.newinfra_service_conf.service_info import dict_service
from conf.newinfra_service_conf.dictionary import dictionary

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

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_const_dict(self, parent_code, locale=None):
        """根据 parent_code 获取常量字典
        :param parent_code: 常量的 parent_code
        """

        if (parent_code is None or
            parent_code not in const.CONSTANT_PARENT_CODE.values()):
            raise ValueError('invalid parent_code')

        params = ObjectDict(parent_code=parent_code)
        response = yield http_get(path.DICT_CONSTANT, params)
        return self.make_const_dict_result(response, parent_code, locale)

    @gen.coroutine
    def get_countries(self, order, locale_display=None):
        """
        获取国家列表
        hot为热门国家
        """

        countries_res = yield http_get(path.DICT_COUNTRY)
        continent_res = yield self.get_const_dict(
            parent_code=const.CONSTANT_PARENT_CODE.CONTINENT)

        return self.make_countries_result(countries_res, continent_res, order, locale_display)

    @gen.coroutine
    def get_country_code_by(self, name=None):
        """从国家名字拿 code，找不到就返回 0"""
        ret = 0
        if not name:
            raise ValueError('name')

        countries_res = yield http_get(path.DICT_COUNTRY, jdata={'name': name})
        result, data = countries_res.status == 0, countries_res.data

        if result and data:
            ret = data[0].get('id')

        return ret

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_sms_country_codes(self, display_locale):
        """获取国家电话区号"""

        countries_res = yield http_get(path.DICT_COUNTRY)
        result, data = unboxing(countries_res)

        res = []
        for country in data:
            if country['sms_enabled']:
                to_append = ObjectDict()
                if display_locale == "en_US":
                    to_append.text = str(country['ename'])
                else:
                    to_append.text = str(country['name'])
                to_append.code_text = str(country['code'])
                #updated by iris
                to_append.icon_class = str(country['icon_class'])
                res.append(to_append)
        return res

    @gen.coroutine
    def get_sms_country_code_list(self):
        """仅获取国家区号列表
        将 86 放在第一个
        """
        countries_res = yield http_get(path.DICT_COUNTRY)

        result, data = unboxing(countries_res)

        code_list = [str(country['code']) for country in data
                     if country['sms_enabled']]

        code_list.insert(0, code_list.pop(code_list.index('86')))

        return code_list

    def make_countries_result(self, countries_res, continent_res, order=None, locale_display=None):
        """获取国籍列表，按某种排序方式整理 """

        filter_keys = ['id', 'name', 'continent_code', 'ename', 'hot_country']
        countries = countries_res.data

        def countries_gen(countries):
            for c in countries:
                d = sub_dict(c, filter_keys)
                d.code = d.id
                if locale_display == "en_US":
                    d.name = d.ename
                d.pop('id', None)
                yield d

        def filter_countries_gen(countries, continent):
            for c in countries:
                if c.continent_code == int(continent[0]):
                    c.pop('continent_code', None)
                    yield c

        countries = list(countries_gen(countries))

        hot_countries = list(filter(
            lambda x: x.get('hot_country') == 1,  # hot_country=1为热门国家
            countries))

        if order == "continent":
            ret = []
            for continent in continent_res.items():
                ret.append(
                    ObjectDict(
                        text=continent[1],
                        list=list(filter_countries_gen(
                            countries, continent))
                    ))
        else:
            ret = self.order_country_by_first_letter(countries, locale_display)
        data = ObjectDict({"hot": hot_countries,
                           "list": ret})
        return data

    @staticmethod
    def order_country_by_first_letter(content, locale_display):
        res, heads = [], []
        for el in content:
            if locale_display == "en_US":
                h = el.get('name')[0] if el.get('name') else el.get('name')
            else:
                h = lazy_pinyin(
                    el.get('name'),
                    style=pypinyin.STYLE_FIRST_LETTER)[0].upper()

            if h not in heads:
                cities_group = ObjectDict(text=h, list=[])
                cities_group.list.append(ObjectDict(el))
                res.append(cities_group)
                heads.append(h)
            else:
                group = list(filter(lambda x: x.text == h, res))[0]
                group.list.append(el)

        ret = sorted(res, key=lambda x: x.text)

        return ret

    @staticmethod
    def make_const_dict_result(http_response, parent_code, locale=None):
        """获取常量字典后的结果处理"""
        res_data = http_response.data
        ret = ObjectDict()
        for el in res_data.get(str(parent_code)):
            el = ObjectDict(el)
            setattr(ret, str(el.code), locale.translate(el.name) if isinstance(el.name, str) and locale else el.name)
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

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_colleges(self):
        """获取所有学校列表"""
        response = yield http_get(path.DICT_COLLEGE)
        return self.make_college_list_result(response)

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_mainland_colleges(self):
        """获取国内所有院校列表"""
        response = yield http_get(path.DICT_MAINLAND_COLLEGE)
        colleges = self.make_college_list_result(response)
        ret = sorted(colleges, key=lambda x: lazy_pinyin(x.get('name'), style=pypinyin.STYLE_FIRST_LETTER)[0].upper())
        data = ObjectDict({"list": ret})
        return data

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_overseas_colleges(self, country_id):
        """根据id获取国外院校列表"""
        data = ObjectDict({
            "country_id": country_id
        })
        response = yield http_get(path.DICT_COLLEGE_BY_ID, jdata=data)
        colleges = response.data
        ret = sorted(colleges, key=lambda x: lazy_pinyin(x.get('name'), style=pypinyin.STYLE_FIRST_LETTER)[0].upper())
        data = ObjectDict({"list": ret})
        return data

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

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_cities(self, locale_display=None, hot=False):
        """获取城市列表
        hot 为 True 为查询热门城市
        """
        level1_cities = yield self._get_level_1_cities()
        level2_cities = yield self._get_level_2_cities()

        return self.make_cities_result(level1_cities, level2_cities, hot, locale_display=locale_display)

    def make_cities_result(self, level1_cities, level2_cities, hot=False, locale_display=None):
        """Merge level1/2 的城市数据，拼装并返回
        hot 为 True 为查询热门城市
        """
        res = level1_cities + level2_cities

        cities, ret, heads = [], [], []

        if locale_display == "en_US":
            sub_name = ['code', 'ename']
        else:
            sub_name = ['code', 'name']
        rename_mapping = {
            'ename': 'name'
        }
        for e in res:
            sub_res = rename_keys(sub_dict(e, sub_name), rename_mapping)
            ret.append(sub_res)

        if hot:
            cities = list(filter(
                lambda x: x.get('code') in self._HOT_CITY_CODES_WECHAT,
                ret))
            return cities

        else:
            for el in ret:
                is_gat = any(
                    map(lambda x: str(el.get('code')).startswith(str(x)),
                        self._GAT_PREFIX))
                if locale_display == "en_US":
                    h = el.get('name')[0] if el.get('name') else el.get('name')
                else:
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

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_hot_cities(self):
        """Alias for get_cities(hot=False) :)"""
        cities = yield self.get_cities(hot=True)
        return cities

    @cache(ttl=60 * 60 * 5)
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

    @cache(ttl=60 * 60 * 5)
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

        http_response1 = yield self._get_level_1_cities()
        http_response2 = yield self._get_level_2_cities()
        http_response = http_response1 + http_response2
        return self.make_city_name_by_code_result(http_response, city_code)

    @staticmethod
    def make_city_name_by_code_result(response, city_code):
        filtered = list(filter(lambda x: x.get('code') == city_code, response))
        if filtered:
            return filtered[0].get('name')
        else:
            return None

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_mars_industries(self):
        """获取Mars行业"""
        ret = yield http_get(path.DICT_INDUSTRY_MARS, dict(parent=0))
        ret = yield self.make_mars_industries_result(ret)
        return ret

    @staticmethod
    @gen.coroutine
    def make_mars_industries_result(http_response):
        res_data = http_response.data
        industries = []
        for el in res_data:
            el = ObjectDict(el)
            out = ObjectDict()
            out.text = el.name
            level2 = yield http_get(path.DICT_INDUSTRY_MARS, dict(parent=el.code))
            out.list = list(map(lambda x: sub_dict(x, ['code', 'name']), level2.data))
            industries.append(out)
        return industries

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_industries(self, level=2, locale_display=None):
        """获取行业
        industries
        level1 + level2
        """
        ret = yield http_get(path.DICT_INDUSTRY, dict(parent=0))
        if level == 2:
            ret = yield self.make_industries_result(ret, locale_display)
        return ret

    @gen.coroutine
    def get_industries_raw(self):
        """获取行业raw数据"""
        ret = yield http_get(path.DICT_INDUSTRY)
        return ret

    @staticmethod
    @gen.coroutine
    def make_industries_result(http_response, locale_display=None):
        res_data = http_response.data
        industries = []
        for el in res_data:
            el = ObjectDict(el)
            out = ObjectDict()
            if locale_display == "en_US":
                sub_name = ['code', 'ename']
                out.text = el.ename
            else:
                sub_name = ['code', 'name']
                out.text = el.name
            level2 = yield http_get(path.DICT_INDUSTRY, dict(parent=el.code))
            rename_mapping = {'ename': 'name'}

            out.list = list(map(lambda x: rename_keys(sub_dict(x, sub_name), rename_mapping), level2.data))
            industries.append(out)
        return industries

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_functions(self, code=0, locale_display=None):
        """获取职能
        Get functions (code=0 -> level1+level2, code!=0 -> level2+level3)
        """
        if not isinstance(code, int):
            raise ValueError('invalid code')

        http_response = yield http_get(path.DICT_POSITION, {})
        return self.get_function_result(http_response, code, locale_display)

    def get_function_result(self, response, code=0, locale_display=None):
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
            level2 = [sub_dict(ObjectDict(f), ['code', 'name']) for f in res_data if
                      f['parent'] == l.code and f['level'] == 2]
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
                L2_res_data = L2_res.data.get(str(e['code']))  # -> list
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

    @gen.coroutine
    def get_comment_tags_by_code(self, code):
        """
        根据不同的推荐人和被推荐人关系获取不同的评价标签
        :param code: 推荐关系编号
        :return:
        """
        res = yield http_get(
            path.DICT_COMMENT_TAGS_BY_CODE,
            jdata=dict(code=code)
        )
        res_data = res.data
        returned_data = [{"zh": item['tag'], "en": item['tag_en']} for item in res_data]
        return returned_data

    @gen.coroutine
    def get_hope_job_tree(self, field_type):
        """
        根据不同的field_type[fileType =109=综合管理培训生项目  传510000 fileType =110=职能管理培训生项目 传520000]获取不同的岗位志愿
        :param field_type: 字段类型
        :return:
        """
        if int(field_type) == 109:
            code_list = 510000
        else:
            code_list = 520000

        params = ObjectDict({
            'code_list': str(code_list)
        })
        res = yield http_get_v2(dictionary.NEWINFRA_DICT_HOPE_JOB_TREE, dict_service, params)
        return res.data

    @gen.coroutine
    def get_dict_regions(self, locale_display=None):
        """
        获取全国的省市
        :param
        :return:
        """
        res = yield http_get_v2(dictionary.NEWINFRA_DICT_REGION, dict_service)
        ret = yield self.make_result(res.data, locale_display)
        return res.data

    @staticmethod
    @gen.coroutine
    def make_result(data, locale_display=None):
        if locale_display == "en_US":
            sub_name = ['code', 'ename']
        else:
            sub_name = ['code', 'name']
        rename_mapping = {'ename': 'name'}

        for province in data:
            for city in province.cities:
                if city.get("cities"):
                    city["cities"] = list(map(lambda x: rename_keys(sub_dict(x, sub_name), rename_mapping), city.get("cities")))

            if province.get("cities"):
                province["cities"] = list(map(lambda x: rename_keys(sub_dict(x, sub_name), rename_mapping), province.get("cities")))
        data = list(map(lambda x: rename_keys(sub_dict(x, sub_name), rename_mapping), data))
        return data

    # return list(
    #     filter(lambda x: x.get('code') in self._LEVEL1_CITY_CODES,
    #            res_data))
