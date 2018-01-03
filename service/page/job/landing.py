# coding=utf-8

import json

from tornado import gen, httpclient

from service.page.base import PageService

from util.common import ObjectDict
from util.tool.str_tool import to_str
from util.tool.dict_tool import sub_dict
from util.tool.str_tool import split, set_literl
from util.tool.iter_tool import list_dedup_list
import conf.common as const

from setting import settings

import conf.platform as platform_const
from util.common.es import BaseES


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
                if isinstance(to_append, list):
                    key_list = key_list + to_append
                else:
                    key_list.append(to_append)

        return key_list

    @gen.coroutine
    def get_positions_data(self, conf_search_seq, company_id, search_condition_dict):
        """ 从 ES 获取全部职位信息
        可以正确解析 salary
        """
        ret = []
        query_size = platform_const.LANDING_QUERY_SIZE

        key_list = []
        value_list = []
        # 默认最多可以附带三个链接筛选条件
        if search_condition_dict:
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
                                {"match": {"company_id": company_id}},
                                {"match": {"status": const.OLD_YES}},
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
                                {"match": {"company_id": company_id}},
                                {"match": {"status": const.OLD_YES}},
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
                                {"match": {"company_id": company_id}},
                                {"match": {"status": const.OLD_YES}},
                                {"match": {key_a: value_a}},
                                {"match": {key_b: value_b}},
                                {"match": {key_c: value_c}}
                            ]
                        }
                    }
                }
            else:
                data = {
                    "size": query_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"company_id": company_id}},
                                {"match": {"status": const.OLD_YES}}
                            ]
                        }
                    }
                }
        else:
            data = {
                "size": query_size,
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"company_id": company_id}},
                            {"match": {"status": const.OLD_YES}}
                            ]
                        }
                    }
                }
        response = self.es.search(index='index', body=data)

        result_list = response.hits.hits

        # 获取筛选项
        key_list = self.make_key_list(conf_search_seq)
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
    def split_cities(data, *, delimiter=None):
        """如果一条数据中包含多个城市，应该分裂成多条数据"""
        ret = []
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
    def make_search_seq(self, company, params):
        """
        生成高级搜索功能中前端需要的数据
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

        # 获取链接上配置的筛选参数
        search_condition_dict = dict()
        all_key_order = [platform_const.LANDING[e].get('form_name') for e in range(0, 9)]
        for key, value in params.items():
            if value and key in all_key_order and key not in key_order:
                search_condition_dict.update(key=value)

        # 默认 conf_search_seq
        if not conf_search_seq:
            conf_search_seq = (
                platform_const.LANDING_INDEX_CITY,
                platform_const.LANDING_INDEX_SALARY,
                platform_const.LANDING_INDEX_CHILD_COMPANY,
                platform_const.LANDING_INDEX_DEPARTMENT
            )

        positions_data = yield self.get_positions_data(conf_search_seq, company.id, search_condition_dict)

        if platform_const.LANDING_INDEX_CITY in conf_search_seq:
            positions_data = self.split_cities(positions_data)

        if platform_const.LANDING_INDEX_CHILD_COMPANY in conf_search_seq:
            positions_data = yield self.append_child_company_name(positions_data)

        self.logger.debug(conf_search_seq)

        # 构建 [{"text": XXX, "value": XXX}, ...] 的形式
        positions_data_values = []
        for e in positions_data:
            to_append = []
            for k in key_order:
                if k == 'child_company_abbr':
                    to_append.append(e.get(k))

                elif k == 'candidate_source_name':
                    to_append.append({"text": e.get(k), "value": const.CANDIDATE_SOURCE_SEARCH_REVERSE.get(e.get(k))})

                elif k == 'employment_type_name':
                    to_append.append({"text": e.get(k), "value": const.EMPLOYMENT_TYPE_SEARCH_REVERSE.get(e.get(k))})
                else:
                    to_append.append({"text": e.get(k), "value": e.get(k)})
            for s in search_condition_dict:
                if s == 'child_company_abbr':
                    to_append.append(e.get(s))

                elif s == 'candidate_source_name':
                    to_append.append({"text": e.get(s), "value": const.CANDIDATE_SOURCE_SEARCH_REVERSE.get(e.get(s))})

                elif s == 'employment_type_name':
                    to_append.append({"text": e.get(s), "value": const.EMPLOYMENT_TYPE_SEARCH_REVERSE.get(e.get(s))})
                else:
                    to_append.append({"text": e.get(s), "value": e.get(s)})
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

            return platform_const.LANDING[search_item].get("chpe")

        return ObjectDict({
            "field_name": [custom_field(e) for e in conf_search_seq],
            "field_form_name": [platform_const.LANDING[e].get("form_name") for e in conf_search_seq],
            "values": dedupped_position_data_values
        })
