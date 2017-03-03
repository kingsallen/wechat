# coding=utf-8


import itertools
import collections

import pypinyin

from tornado.util import ObjectDict
import tornado.gen as gen
import conf.path as path
from util.tool.http_tool import http_get
from util.tool.dict_tool import sub_dict
from util.common.decorator import cache

from service.data.base import DataService


class DictDataService(DataService):

    CONSTANT_TYPES = ObjectDict(
        COMPANY_TYPE=1101,          # 公司类型
        COMPANY_SCALE=1102,         # 公司规模
        COMPANY_PROPERTY=1103,      # 公司性质
        DEGREE_POSITION=2101,       # 公司职位要求学历
        GENDER_POSITION=2102,       # 性别
        JOB_TYPE=2103,              # 工作性质
        EMPLOYMENT_TYPE=2104,       # 招聘类型
        PRIVACY_POLICY=3101,        # 隐私策略
        WORK_STATUS=3102,           # 工作状态
        POLITIC_STATUS=3103,        # 政治面貌
        DEGREE_USER=3104,           # 用户学历
        WORK_INTENTION=3105,        # 求职意愿-工作类型
        TIME_TO_BE_ON_BOARD=3106,   # 到岗时间
        WORKDAYS_PER_WEEK=3107,     # 每周到岗时间
        LANGUAGE_FRUENCY=3108,      # 语言能力-掌握程度
        GENDER_USER=3109,           # 性别
        MARRIAGE_STATUS=3110,       # 婚姻情况
        ID_TYPE=3111,               # 证件类型
        RECIDENCE_TYPE=3112,        # 户口类型
        MAJOR_RANK=3113,            # 专业排名
        CURRENT_SALARY_MONTH=3114,  # 当前月薪
        CURRENT_SALARY_YEAR=3115,   # 当前年薪
        CAN_ON_SITE=3116,           # 是否接受出差
        WORK_ROTATION=3117,         # 选择班次
        PROFILE_IMPORT_SOURCE=3118, # Profile来源
        PROFILE_SOURCE=3119,        # Profile创建来源
        REGISTER_SOURCE=4101,       # 用户注册来源(source)
    )

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

    @cache(ttl= 60 * 60 * 5)
    @gen.coroutine
    def get_const_dict(self, parent_code):
        """根据 parent_code 获取常量字典
        :param parent_code: 常量的 parent_code
        """

        # 参数校验
        if (parent_code is None or
                parent_code not in self.CONSTANT_TYPES.values()):
            raise ValueError('invalid parent_code')

        params = ObjectDict(parent_code=parent_code)

        res = (yield http_get(path.DICT_CONSTANT, params)).data

        ret = ObjectDict()
        for el in res.get(str(parent_code)):
            el = ObjectDict(el)
            setattr(ret, str(el.code), el.name)

        ret = collections.OrderedDict(sorted(ret.items()))
        return ret

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_colleges(self):
        """获取学校列表"""

        collegecode_list = []
        res = (yield http_get(path.DICT_COLLEGE, {})).data

        if isinstance(res, list):
            collegecode_nested_list = list(itertools.chain(
                map(lambda x: x.get("children", []), res)))
            for cn_list in collegecode_nested_list:
                for pair in cn_list:
                    collegecode_list.append(pair)

        return collegecode_list

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_college_code_by_name(self, school_name):
        """根据学校名称返回学校 code"""

        if school_name is None or not isinstance(school_name, str):
            raise ValueError('invalid school_name')

        colleges = yield self.get_colleges()

        ret = list(filter(lambda x: x.get('name') == school_name,
                          colleges))

        if ret:
            code = ret[0].get('code', 0)
        else:
            code = 0

        return code

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def _get_level_1_cities(self):
        """获取一级城市列表"""
        params = dict(level=1, is_using=1)
        res = (yield http_get(path.DICT_CITIES, params)).data
        return list(
            filter(lambda x: x.get('code') in self._LEVEL1_CITY_CODES, res))

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def _get_level_2_cities(self):
        """获取二级城市列表"""
        params = dict(level=2, is_using=1)
        res = (yield http_get(path.DICT_CITIES, params)).data
        return res

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_cities(self, hot=False):
        """获取城市列表
        If hot is True the function only returns hot cities
        cities are grouped by first pinyin letter
        """

        cities1 = yield self._get_level_1_cities()
        cities2 = yield self._get_level_2_cities()

        res = cities1 + cities2

        # merge
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

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_hot_cities(self):
        """alias for get_cities(hot=False) :)"""
        cities = yield self.get_cities(hot=True)
        return cities

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_city_code_by(self, city_name):
        """city city_name -> code
        :param city_name: city name, type: str
        :return: city code or 0 if city_name is not found
        """
        if city_name is None or not isinstance(city_name, str):
            raise ValueError('invalid city_name')

        res = yield http_get(path.DICT_CITIES, dict(level=2))

        filtered = list(filter(lambda x: x.get('name') == city_name, res))
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

        res = yield http_get(path.DICT_CITIES, dict(level=2))

        filtered = list(filter(lambda x: x.get('code') == city_code, res))
        if filtered:
            return filtered[0].get('name')
        else:
            return None

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_industries(self):
        """获取行业
        industries
        level1 + level2
        """

        level1 = (yield http_get(path.DICT_INDUSTRY, dict(parent=0))).data
        industries = []

        for el in level1:
            el = ObjectDict(el)
            out = ObjectDict()
            out.text = el.name
            level2 = (
                yield http_get(path.DICT_INDUSTRY, dict(parent=el.code))).data
            out.list = list(map(lambda x: sub_dict(x, ['code', 'name']), level2))
            industries.append(out)

        return industries

    @cache(ttl=60 * 60 * 5)
    @gen.coroutine
    def get_function(self, code=0):
        """获取职能
        Get functions (code=0 -> level1+level2, code!=0 -> level2+level3)
        """

        params = dict(parent=code)

        @cache(ttl= 60 * 60 * 5)
        @gen.coroutine
        def _get_funcs():
            bunch = (yield http_get(path.DICT_POSITION, params)).data
            ret = []
            for b in bunch:
                b = ObjectDict(b)
                if code:
                    o = ObjectDict(sub_dict(b, ['code', 'name']))
                else:
                    o = ObjectDict()
                    o.text = b.name
                    params.update(parent=b.get('code'))

                    level2 = (yield http_get(path.DICT_POSITION, params)).data
                    o.list = list(map(
                        lambda x: sub_dict(x, ['code', 'name']), level2))

                ret.append(o)
            return ret

        # 这么写是因为原先需要缓存部分返回的信息。
        # 现在不用了，直接调用内部函数
        functions = yield _get_funcs()
        return functions
