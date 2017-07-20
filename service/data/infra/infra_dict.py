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

    @cache(ttl=60*60*5)
    @gen.coroutine
    def get_countries(self):
        """获取国家列表"""

        countries_res = yield http_get(path.DICT_COUNTRY)
        continent_res = yield self.get_const_dict(
            parent_code=const.CONSTANT_PARENT_CODE.CONTINENT)

        return self.make_countries_result(countries_res, continent_res)

    @staticmethod
    def make_countries_result(countries_res, continent_res):
        """获取国籍列表，按大洲分割

        [{'list': [{'code': 1, 'name': '阿富汗'},
           {'code': 11, 'name': '亚美尼亚'},
           {'code': 15, 'name': '阿塞拜疆'},
           {'code': 17, 'name': '巴林'},
           {'code': 18, 'name': '孟加拉'},
           {'code': 25, 'name': '不丹'},
           {'code': 31, 'name': '文莱'},
           {'code': 35, 'name': '柬埔寨'},
           {'code': 43, 'name': '中国'},
           {'code': 44, 'name': '圣诞岛'},
           {'code': 45, 'name': '科科斯(基林)群岛'},
           {'code': 56, 'name': '塞浦路斯'},
           {'code': 77, 'name': '格鲁吉亚共和国'},
           {'code': 93, 'name': '香港'},
           {'code': 96, 'name': '印度共和国'},
           {'code': 97, 'name': '印度尼西亚共和国'},
           {'code': 98, 'name': '伊朗伊斯兰共和国'},
           {'code': 99, 'name': '伊拉克共和国'},
           {'code': 102, 'name': '以色列国'},
           {'code': 105, 'name': '日本'},
           {'code': 107, 'name': '约旦哈希姆王国'},
           {'code': 108, 'name': '哈萨克斯坦共和国'},
           {'code': 111, 'name': '朝鲜民主主义人民共和国'},
           {'code': 112, 'name': '韩国'},
           {'code': 113, 'name': '科威特国'},
           {'code': 114, 'name': '吉尔吉斯共和国'},
           {'code': 115, 'name': '老挝人民民主共和国'},
           {'code': 117, 'name': '黎巴嫩共和国'},
           {'code': 124, 'name': '澳门'},
           {'code': 128, 'name': '马来西亚'},
           {'code': 129, 'name': '马尔代夫共和国'},
           {'code': 140, 'name': '蒙古国'},
           {'code': 145, 'name': '缅甸联邦'},
           {'code': 148, 'name': '尼伯尔王国'},
           {'code': 158, 'name': '阿曼'},
           {'code': 159, 'name': '巴基斯坦伊斯兰共和国'},
           {'code': 161, 'name': '巴勒斯坦'},
           {'code': 166, 'name': '菲律宾共和国'},
           {'code': 171, 'name': '卡塔尔国'},
           {'code': 186, 'name': '沙特阿拉伯王国'},
           {'code': 191, 'name': '新加坡'},
           {'code': 200, 'name': '斯里兰卡民主社会主义共和国'},
           {'code': 207, 'name': '阿拉伯叙利亚共和国'},
           {'code': 208, 'name': '台湾'},
           {'code': 209, 'name': '塔吉克斯坦共和国'},
           {'code': 211, 'name': '泰国'},
           {'code': 212, 'name': '东帝汶'},
           {'code': 218, 'name': '土耳其共和国'},
           {'code': 219, 'name': '土库曼斯坦'},
           {'code': 224, 'name': '阿拉伯联合酋长国'},
           {'code': 228, 'name': '乌兹别克斯坦共和国'},
           {'code': 231, 'name': '越南社会主义共和国'},
           {'code': 236, 'name': '也门共和国'}],
  'text': '亚洲'},
 {'list': [{'code': 7, 'name': '安圭拉'},
           {'code': 9, 'name': '安提瓜和巴布达'},
           {'code': 12, 'name': '阿鲁巴'},
           {'code': 16, 'name': '巴哈马'},
           {'code': 19, 'name': '巴巴多斯'},
           {'code': 22, 'name': '伯利兹'},
           {'code': 24, 'name': '百慕大'},
           {'code': 37, 'name': '加拿大'},
           {'code': 39, 'name': '开曼群岛'},
           {'code': 51, 'name': '哥斯达黎加'},
           {'code': 54, 'name': '古巴'},
           {'code': 55, 'name': '库拉索岛'},
           {'code': 60, 'name': '多米尼克'},
           {'code': 61, 'name': '多米尼加'},
           {'code': 64, 'name': '萨尔瓦多'},
           {'code': 82, 'name': '格陵兰'},
           {'code': 83, 'name': '格林纳达'},
           {'code': 85, 'name': '危地马拉'},
           {'code': 90, 'name': '海地'},
           {'code': 92, 'name': '洪都拉斯'},
           {'code': 104, 'name': '牙买加'},
           {'code': 136, 'name': '墨西哥'},
           {'code': 142, 'name': '蒙特塞拉特'},
           {'code': 162, 'name': '巴拿马'},
           {'code': 170, 'name': '波多黎各'},
           {'code': 178, 'name': '圣基茨和尼维斯'},
           {'code': 179, 'name': '圣卢西亚'},
           {'code': 180, 'name': '圣马丁'},
           {'code': 181, 'name': '圣皮埃尔和密克隆'},
           {'code': 182, 'name': '圣文森特和格林纳丁斯'},
           {'code': 192, 'name': '荷属圣马丁'},
           {'code': 216, 'name': '特立尼达和多巴哥'},
           {'code': 220, 'name': '特克斯和凯科斯群岛'},
           {'code': 226, 'name': '美国'},
           {'code': 232, 'name': '英属维尔京群岛'},
           {'code': 233, 'name': '美属维尔京群岛'}],
  'text': '北美洲'},
 {'list': [{'code': 2, 'name': '阿尔巴尼亚'},
           {'code': 5, 'name': '安道尔公国'},
           {'code': 14, 'name': '奥地利'},
           {'code': 20, 'name': '白俄罗斯'},
           {'code': 21, 'name': '比利时'},
           {'code': 27, 'name': '波斯尼亚和黑塞哥维那共和国'},
           {'code': 32, 'name': '保加利亚'},
           {'code': 53, 'name': '克罗地亚'},
           {'code': 57, 'name': '捷克'},
           {'code': 58, 'name': '丹麦'},
           {'code': 67, 'name': '爱沙尼亚'},
           {'code': 70, 'name': '法罗群岛'},
           {'code': 72, 'name': '芬兰'},
           {'code': 73, 'name': '法国'},
           {'code': 78, 'name': '德国'},
           {'code': 80, 'name': '直布罗陀'},
           {'code': 81, 'name': '希腊'},
           {'code': 86, 'name': '根西'},
           {'code': 91, 'name': '梵蒂冈城国'},
           {'code': 94, 'name': '匈牙利'},
           {'code': 95, 'name': '冰岛'},
           {'code': 100, 'name': '爱尔兰'},
           {'code': 101, 'name': '马恩岛'},
           {'code': 103, 'name': '意大利'},
           {'code': 106, 'name': '泽西岛'},
           {'code': 116, 'name': '拉脱维亚'},
           {'code': 121, 'name': '列支敦士登'},
           {'code': 122, 'name': '立陶宛'},
           {'code': 123, 'name': '卢森堡'},
           {'code': 125, 'name': '马其顿'},
           {'code': 131, 'name': '马耳他'},
           {'code': 138, 'name': '摩尔多瓦'},
           {'code': 139, 'name': '摩纳哥'},
           {'code': 141, 'name': '黑山'},
           {'code': 149, 'name': '荷兰'},
           {'code': 157, 'name': '挪威'},
           {'code': 168, 'name': '波兰'},
           {'code': 169, 'name': '葡萄牙'},
           {'code': 173, 'name': '罗马尼亚'},
           {'code': 174, 'name': '俄罗斯联邦'},
           {'code': 184, 'name': '圣马力诺'},
           {'code': 188, 'name': '塞尔维亚'},
           {'code': 193, 'name': '斯洛伐克'},
           {'code': 194, 'name': '斯洛文尼亚'},
           {'code': 199, 'name': '西班牙'},
           {'code': 205, 'name': '瑞典'},
           {'code': 206, 'name': '瑞士联邦'},
           {'code': 223, 'name': '乌克兰'},
           {'code': 225, 'name': '英国'},
           {'code': 240, 'name': '科索沃'}],
  'text': '欧洲'},
 {'list': [{'code': 4, 'name': '美属萨摩亚'},
           {'code': 13, 'name': '澳大利亚'},
           {'code': 50, 'name': '库克群岛'},
           {'code': 71, 'name': '斐济'},
           {'code': 74, 'name': '法属波利尼西亚'},
           {'code': 84, 'name': '关岛'},
           {'code': 110, 'name': '基里巴斯'},
           {'code': 132, 'name': '马绍尔群岛'},
           {'code': 137, 'name': '密克罗尼西亚'},
           {'code': 147, 'name': '瑙鲁'},
           {'code': 150, 'name': '新喀里多尼亚'},
           {'code': 151, 'name': '新西兰'},
           {'code': 155, 'name': '纽埃'},
           {'code': 156, 'name': '北马里亚纳'},
           {'code': 160, 'name': '帕劳'},
           {'code': 163, 'name': '巴布亚新几内亚'},
           {'code': 167, 'name': '皮特凯恩'},
           {'code': 183, 'name': '西萨摩亚'},
           {'code': 195, 'name': '所罗门群岛'},
           {'code': 214, 'name': '托克劳'},
           {'code': 215, 'name': '汤加'},
           {'code': 221, 'name': '图瓦卢'},
           {'code': 229, 'name': '瓦努阿图'},
           {'code': 234, 'name': '瓦利斯和富图纳群岛'}],
  'text': '大洋洲'},
 {'list': [{'code': 10, 'name': '阿根廷'},
           {'code': 26, 'name': '玻利维亚'},
           {'code': 29, 'name': '巴西'},
           {'code': 42, 'name': '智利'},
           {'code': 46, 'name': '哥伦比亚'},
           {'code': 62, 'name': '厄瓜多尔'},
           {'code': 89, 'name': '圭亚那'},
           {'code': 164, 'name': '巴拉圭'},
           {'code': 165, 'name': '秘鲁'},
           {'code': 202, 'name': '苏里南'},
           {'code': 227, 'name': '乌拉圭'},
           {'code': 230, 'name': '委内瑞拉'},
           {'code': 239, 'name': '荷属安的列斯'}],
  'text': '南美洲'},
 {'list': [{'code': 3, 'name': '阿尔及利亚'},
           {'code': 6, 'name': '安哥拉'},
           {'code': 23, 'name': '贝宁'},
           {'code': 28, 'name': '博茨瓦纳'},
           {'code': 33, 'name': '布基纳法索'},
           {'code': 34, 'name': '布隆迪'},
           {'code': 36, 'name': '喀麦隆'},
           {'code': 38, 'name': '佛得角'},
           {'code': 40, 'name': '中非'},
           {'code': 41, 'name': '乍得'},
           {'code': 47, 'name': '科摩罗'},
           {'code': 48, 'name': '刚果民主共和国'},
           {'code': 49, 'name': '刚果'},
           {'code': 52, 'name': '科特迪瓦'},
           {'code': 59, 'name': '吉布提'},
           {'code': 63, 'name': '阿拉伯埃及'},
           {'code': 65, 'name': '赤道几内亚'},
           {'code': 66, 'name': '厄立特里亚'},
           {'code': 68, 'name': '埃塞俄比亚'},
           {'code': 75, 'name': '加蓬'},
           {'code': 76, 'name': '冈比亚'},
           {'code': 79, 'name': '加纳'},
           {'code': 87, 'name': '几内亚比绍'},
           {'code': 88, 'name': '几内亚'},
           {'code': 109, 'name': '肯尼亚'},
           {'code': 118, 'name': '莱索托王国'},
           {'code': 119, 'name': '利比里亚共和国'},
           {'code': 120, 'name': '大阿拉伯利比亚人民社会主义民众国'},
           {'code': 126, 'name': '马达加斯加共和国'},
           {'code': 127, 'name': '马拉维共和国'},
           {'code': 130, 'name': '马里共和国'},
           {'code': 133, 'name': '毛里塔尼亚伊斯兰共和国'},
           {'code': 134, 'name': '毛里求斯共和国'},
           {'code': 135, 'name': '马约特'},
           {'code': 143, 'name': '摩洛哥王国'},
           {'code': 144, 'name': '莫桑比克共和国'},
           {'code': 146, 'name': '纳米比亚共和国'},
           {'code': 153, 'name': '尼日利亚联邦共和国'},
           {'code': 154, 'name': '尼日尔共和国'},
           {'code': 175, 'name': '卢旺达共和国'},
           {'code': 177, 'name': '圣赫勒拿'},
           {'code': 185, 'name': '圣多美和普林西比民主'},
           {'code': 187, 'name': '塞内加尔共和国'},
           {'code': 189, 'name': '塞舌尔共和国'},
           {'code': 190, 'name': '塞拉利昂共和国'},
           {'code': 196, 'name': '索马里共和国'},
           {'code': 197, 'name': '南非共和国'},
           {'code': 198, 'name': '南苏丹共和国'},
           {'code': 201, 'name': '苏丹共和国'},
           {'code': 204, 'name': '斯威士兰王国'},
           {'code': 210, 'name': '坦桑尼亚联合共和国'},
           {'code': 213, 'name': '多哥共和国'},
           {'code': 217, 'name': '突尼斯共和国'},
           {'code': 222, 'name': '乌干达共和国'},
           {'code': 235, 'name': '西撒哈拉'},
           {'code': 237, 'name': '赞比亚共和国'},
           {'code': 238, 'name': '津巴布韦共和国'}],
  'text': '非洲'}]
        """

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
