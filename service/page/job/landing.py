# coding=utf-8

from tornado import gen
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.dict_tool import sub_dict
from util.tool.str_tool import split, set_literl
from util.tool.iter_tool import list_dedup_list
import conf.common as const
import re
import conf.platform as platform_const
from util.common.es import BaseES
from pypinyin import lazy_pinyin
import pypinyin


class LandingPageService(PageService):

    es = BaseES()

    def __init__(self):
        super().__init__()

    @staticmethod
    def make_key_list(conf_search_seq):
        """ 根据 conf_search_seq 来生成 key list
        :param conf_search_seq:
        :return: key_list
        """

        key_list = []
        for key in conf_search_seq:
            to_append = platform_const.LANDING.get(key)
            if to_append:
                to_append = to_append.key
                if isinstance(to_append, list):  # salary
                    for k in to_append:
                    to_append = platform_const.LANDING_ES_KEY_MAP.get(to_append.key)
                    key_list = key_list + to_append
                else:
                    key_list.append(to_append)

        return key_list

    @gen.coroutine
    def get_positions_data(self, conf_search_seq, company_id, search_condition_dict, salary_dict, display_locale, is_referral):
        """ 从 ES 获取全部职位信息
        可以正确解析 salary
        """
        # todo es的搜索语句重构掉，使用dict的update，不要直接写死dict
        ret = []
        query_size = platform_const.LANDING_QUERY_SIZE

        key_list = []
        value_list = []

        data = {
            "size": query_size,
            "query": {
                "bool": {
                    "must": [
                        {"match": {"position.companyId": company_id}},
                        {"match": {"position.status": const.OLD_YES}}
                    ]
                }
            }
        }
        # occupation使用term搜索
        pop_occupation = False
        occupation_value = ''
        if search_condition_dict:
            for key, value in search_condition_dict.items():
                if key == 'occupation':
                    pop_occupation = True
                    occupation_value = value
            if pop_occupation:
                search_condition_dict.pop("occupation")

        # 默认最多可以附带三个链接筛选条件
        if search_condition_dict and not salary_dict:
            for key, value in search_condition_dict.items():
                key_list.append(key)
                value_list.append(value)
            if len(key_list) == 1:
                key_a, value_a = key_list[0], value_list[0]

                data = {
                    "size": query_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"position.companyId": company_id}},
                                {"match": {"position.status": const.OLD_YES}},
                                {"match": {key_a: value_a}}
                            ]
                        }
                    }
                }
            elif len(key_list) == 2:
                key_a, value_a = key_list[0], value_list[0]
                key_b, value_b = key_list[1], value_list[1]

                data = {
                    "size": query_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"position.companyId": company_id}},
                                {"match": {"position.status": const.OLD_YES}},
                                {"match": {key_a: value_a}},
                                {"match": {key_b: value_b}}
                            ]
                        }
                    }
                }
            elif len(key_list) == 3:
                key_a, value_a = key_list[0], value_list[0]
                key_b, value_b = key_list[1], value_list[1]
                key_c, value_c = key_list[2], value_list[2]

                data = {
                    "size": query_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"position.companyId": company_id}},
                                {"match": {"position.status": const.OLD_YES}},
                                {"match": {key_a: value_a}},
                                {"match": {key_b: value_b}},
                                {"match": {key_c: value_c}}
                            ]
                        }
                    }
                }
        elif search_condition_dict and salary_dict:
            for key, value in search_condition_dict.items():
                key_list.append(key)
                value_list.append(value)
            if len(key_list) == 1:
                key_a, value_a = key_list[0], value_list[0]

                data = {
                    "size": query_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"position.companyId": company_id}},
                                {"match": {"position.status": const.OLD_YES}},
                                {"match": {key_a: value_a}}
                            ],
                            "should": [
                                {"range": {"salaryData.salaryTop": {"lte": salary_dict.get('salary_top'), "gte": salary_dict.get('salary_bottom')}}},
                                {"range": {"salaryData.salaryBottom": {"lte": salary_dict.get('salary_top'), "gte": salary_dict.get('salary_bottom')}}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                }
            elif len(key_list) == 2:
                key_a, value_a = key_list[0], value_list[0]
                key_b, value_b = key_list[1], value_list[1]

                data = {
                    "size": query_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"position.companyId": company_id}},
                                {"match": {"position.status": const.OLD_YES}},
                                {"match": {key_a: value_a}},
                                {"match": {key_b: value_b}}
                            ],
                            "should": [
                                {"range": {"salaryData.salaryTop": {"lte": salary_dict.get('salary_top'), "gte": salary_dict.get('salary_bottom')}}},
                                {"range": {"salaryData.salaryBottom": {"lte": salary_dict.get('salary_top'), "gte": salary_dict.get('salary_bottom')}}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                }
        elif salary_dict and not search_condition_dict:
            data = {
                "size": query_size,
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"position.companyId": company_id}},
                            {"match": {"position.status": const.OLD_YES}}
                        ],
                        "should": [
                            {"range": {"salaryData.salaryTop": {"lte": salary_dict.get('salary_top'), "gte": salary_dict.get('salary_bottom')}}},
                            {"range": {"salaryData.salaryBottom": {"lte": salary_dict.get('salary_top'), "gte": salary_dict.get('salary_bottom')}}}
                        ],
                        "minimum_should_match": 1
                    }
                }
            }
        if is_referral:
            data.get("query").get("bool").get("must").append({"match": {"is_referral": const.YES}})
        if pop_occupation:
            data.get("query").get("bool").get("must").append({"term": {"search_data.occupation": occupation_value}})
        self.logger.debug(data)
        response = self.es.search(index='newpositions', body=data)

        result_list = response.hits.hits
        self.logger.debug(result_list)

        # 获取筛选项
        key_list = self.make_key_list(conf_search_seq)
        if display_locale == "en_US" and "city" in key_list:
            key_list.remove("city")
            key_list.append("city_ename")
        self.logger.debug("key_list: %s" % key_list)

        for e in result_list:
            source = e.get("_source")

            # 使用 key_list 来筛选 source
            source = ObjectDict(sub_dict(source, key_list))

            if 'salary_top' in key_list:
                # 对 salary 做特殊处理 (salary_top, salary_bottom) -> salary
                salary = [
                    v.get("name") for v in platform_const.SALARY.values()
                    if v.salary_bottom == source.salary_bottom and
                    v.salary_top == source.salary_top
                    ]

                source.salary = salary[0] if salary else ''
                source.pop("salary_top", None)
                source.pop("salary_bottom", None)

            ret.append(source)

        return ret

    @staticmethod
    def split_cities(data, *, delimiter=None, display_locale=None):
        """如果一条数据中包含多个城市，应该分裂成多条数据"""
        ret = []
        if display_locale == "en_US":
            key_to_split = 'city_ename'
        else:
            key_to_split = 'city'
        if not delimiter:
            delimiter = [",", "，"]

        for e in data:
            e = ObjectDict(e)
            value_to_split = e.get(key_to_split)
            if value_to_split:
                splitted_items = split(value_to_split, delimiter)
                if len(splitted_items) > 1:
                    for item in splitted_items:
                        new_e = e.copy()
                        new_e[key_to_split] = item
                        ret.append(ObjectDict(new_e))
                else:
                    ret.append(e)
            else:
                ret.append(e)
        return ret

    @gen.coroutine
    def append_child_company_name(self, data):
        """ 对position_data 添加子公司简称 """

        child_company_ids = list(set([v.publisher_company_id for v in data]))
        if child_company_ids:
            child_company_id_abbr_list = yield self.hr_company_ds.get_companys_list(
                conds="id in " + set_literl(child_company_ids),
                fields=["id", "abbreviation"]
            )
            child_company_id_abbr_dict = {
                e.id: e.abbreviation for e in child_company_id_abbr_list
                }

            for d in data:
                if d.publisher_company_id:
                    d.child_company_abbr = {
                        "text": child_company_id_abbr_dict.get(d.publisher_company_id, ""),
                        "value": d.publisher_company_id
                    }
                else:
                    d.child_company_abbr = ObjectDict()

        return data

    @gen.coroutine
    def make_search_seq(self, company, params, locale, display_locale, is_referral):
        """
        生成高级搜索功能中前端需要的数据
        :param display_locale:
        :param locale:
        :param params:
        :param company:
        :return: {"field_name": ['地点', '子公司', '部门'],
                  "field_form_name": ['city', '...', 'team_name']
                  "values": [[{"text": '上海', "value": "上海"}, ...],
                             [...],
                             ...]
                 }
        """
        conf_search_seq = tuple([int(e.index) for e in company.get("conf_search_seq")])

        key_order = [platform_const.LANDING[kn].get("display_key") for kn in conf_search_seq]
        form_name = [platform_const.LANDING[kn].get("form_name") for kn in conf_search_seq]
        # 获取链接上配置的筛选参数
        display_key_dict = dict()
        salary_dict = dict()
        all_form_name = [platform_const.LANDING[e].get('form_name') for e in range(1, 11)]
        all_key_order = [[platform_const.LANDING[e].get("display_key"), platform_const.LANDING[e].get('form_name')] for e in range(1, 10)]
        self.logger.debug('key_order: %s,form_name: %s,all_key_order: %s,all_form_name: %s' % (key_order, form_name, all_key_order, all_form_name))
        for key, value in params.items():
            if value and key in all_form_name and key not in form_name:
                # 将链接参数转换为过滤搜索结果参数
                if key == 'salary':
                    salary_dict['salary_bottom'] = re.search('(^[1-9]\d*)k-([1-9]\d*)k', value).group(1) if re.search('(^[1-9]\d*)k-([1-9]\d*)k', value).group(1) else 0
                    salary_dict['salary_top'] = re.search('(^[1-9]\d*)k-([1-9]\d*)k', value).group(2) if re.search('(^[1-9]\d*)k-([1-9]\d*)k', value).group(2) else 150
                elif key == 'did':
                    key = 'publisher_company_id'
                elif key == 'degree':
                    key = 'degree_name'
                elif key == 'position_type':
                    key = 'notOffice'
                display_key_dict[key] = value
        self.logger.debug(display_key_dict)

        # 链接所带参数
        conf_search_seq_append = []
        for index in range(1, 11):
            for s in display_key_dict.keys():
                if platform_const.LANDING[index].get("key") == s:
                    conf_search_seq_append.append(index)

        if 'salary' in display_key_dict:
            display_key_dict.pop('salary')

        # 重新整理查询条件
        conf_search_seq_plus = tuple([int(e.index) for e in company.get("conf_search_seq")] + conf_search_seq_append)

        # 默认 conf_search_seq
        if not conf_search_seq_plus:
            conf_search_seq_plus = (
                platform_const.LANDING_INDEX_CITY,
                platform_const.LANDING_INDEX_SALARY,
                platform_const.LANDING_INDEX_DEPARTMENT
            )

        positions_data = yield self.get_positions_data(conf_search_seq_plus, company.id, display_key_dict, salary_dict, display_locale, is_referral)

        if platform_const.LANDING_INDEX_CITY in conf_search_seq_plus:
            positions_data = self.split_cities(positions_data, display_locale=display_locale)

        if platform_const.LANDING_INDEX_CHILD_COMPANY in conf_search_seq and platform_const.LANDING_INDEX_CHILD_COMPANY in conf_search_seq_plus:
            positions_data = yield self.append_child_company_name(positions_data)

        self.logger.debug("conf_search_seq_plus:{}".format(conf_search_seq_plus))

        def pinyin_initials(field):
            en = ""
            if field and type(field) != int:
                en = lazy_pinyin(field, style=pypinyin.INITIALS, strict=False)
            return en
        # 构建 [{"text": XXX, "value": XXX}, ...] 的形式
        positions_data_values = []
        for e in positions_data:
            to_append = []
            for k in key_order:
                if k == 'child_company_abbr':
                    c_com = e.get(k)
                    en = pinyin_initials(c_com.get("text"))
                    c_com.update(en=en[0] if en else "")
                    to_append.append(c_com)

                elif k == 'candidate_source_name':
                    text = locale.translate(const.CANDIDATE_SOURCE_SEARCH_LOCALE.get(e.get(k))) if e.get(k) else e.get(k)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": const.CANDIDATE_SOURCE_SEARCH_REVERSE.get(e.get(k)),
                                      "en": en[0] if en else ""})

                elif k == 'employment_type_name':
                    text = locale.translate(const.EMPLOYMENT_TYPE_SEARCH_LOCALE.get(e.get(k))) if e.get(k) else e.get(
                        k)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": const.EMPLOYMENT_TYPE_SEARCH_REVERSE.get(e.get(k)),
                                      "en": en[0] if en else ""})

                elif k == 'degree_name':
                    content = e.get(k)
                    if "及以上" in content:
                        content = content.rstrip("及以上")
                        text = locale.translate(const.DEGREE_SEARCH_LOCALE.get(content.rstrip("及以上")))
                    else:
                        text = locale.translate(const.DEGREE_SEARCH_LOCALE.get(e.get(k))) if e.get(k) else e.get(
                            k)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": content,
                                      "en": en[0] if en else ""})
                elif k == 'city':
                    text = e.get('city_ename') if display_locale == 'en_US' else e.get(k)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": text,
                                      "en": en[0] if en else ""})
                else:
                    en = pinyin_initials(e.get(k))
                    to_append.append({"text": e.get(k), "value": e.get(k), "en": en[0] if en else ""})
            # 将链接参数拼接进筛选条件列表
            for s in display_key_dict:
                if s == 'child_company_abbr':
                    c_com = e.get(s)
                    en = pinyin_initials(c_com.get("text"))
                    c_com.update(en=en[0] if en else "")
                    to_append.append(c_com)

                elif s == 'candidate_source_name':
                    text = locale.translate(const.CANDIDATE_SOURCE_SEARCH_LOCALE.get(e.get(s))) if e.get(s) else e.get(
                        s)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": const.CANDIDATE_SOURCE_SEARCH_REVERSE.get(e.get(s)),
                                      "en": en[0] if en else ""})

                elif s == 'employment_type_name':
                    text = locale.translate(const.CANDIDATE_SOURCE_SEARCH_LOCALE.get(e.get(s))) if e.get(s) else e.get(
                        s)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": const.EMPLOYMENT_TYPE_SEARCH_REVERSE.get(e.get(s)),
                                      "en": en[0] if en else ""})
                elif s == 'degree_name':
                    content = e.get(s)
                    if "及以上" in content:
                        content = content.rstrip("及以上")
                        text = locale.translate(const.DEGREE_SEARCH_LOCALE.get(content.rstrip("及以上")))
                    else:
                        text = locale.translate(const.DEGREE_SEARCH_LOCALE.get(e.get(s))) if e.get(s) else e.get(
                            s)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": content,
                                      "en": en[0] if en else ""})
                elif s == 'city':
                    text = e.get('city_ename') if display_locale == 'en_US' else e.get(s)
                    en = pinyin_initials(text)
                    to_append.append({"text": text, "value": text,
                                      "en": en[0] if en else ""})
                else:
                    en = pinyin_initials(e.get(s))
                    to_append.append({"text": e.get(s), "value": e.get(s),
                                      "en": en[0] if en else ""})
            positions_data_values.append(to_append)

        # 将构建出来的结果去重，作为返回中的 values 属性
        dedupped_position_data_values = list_dedup_list(positions_data_values)

        # 职位自定义字段/部门自定义/职位职能自定义
        def custom_field(search_item):
            if search_item == platform_const.LANDING_INDEX_OCCUPATION and company.conf_job_occupation:
                return company.conf_job_occupation
            if search_item == platform_const.LANDING_INDEX_CUSTOM and company.conf_job_custom_title:
                return company.conf_job_custom_title
            if search_item == platform_const.LANDING_INDEX_DEPARTMENT and company.conf_teamname_custom.teamname_custom:
                return company.conf_teamname_custom.teamname_custom

            return locale.translate(const.SEARCH_CONDITION.get(str(search_item)))

        return ObjectDict({
            "field_name": [custom_field(e) for e in conf_search_seq_plus],
            "field_form_name": [platform_const.LANDING[e].get("form_name") for e in conf_search_seq],
            "values": dedupped_position_data_values
        })
