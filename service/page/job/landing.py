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


class LandingPageService(PageService):

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
    def get_positions_data(self, conf_search_seq, company_id):
        """ 从 ES 获取全部职位信息
        可以正确解析 salary
        """
        ret = []
        query_size = platform_const.LANDING_QUERY_SIZE

        # 在此调用 ES 的 HTTP GET 搜索接口
        url = settings.es + "/index/_search?company_id:%s+AND+status:%s+AND+size=%s" % (company_id, const.OLD_YES, query_size)
        response = yield httpclient.AsyncHTTPClient().fetch(url)

        body = ObjectDict(json.loads(to_str(response.body)))
        result_list = body.hits.hits

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
    def split_cities(data, delimiter=None):
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
                d.child_company_abbr = {}

        return data

    @gen.coroutine
    def make_search_seq(self, company):
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

        if not conf_search_seq:
            conf_search_seq = (
                platform_const.LANDING_INDEX_CITY,
                platform_const.LANDING_INDEX_SALARY,
                platform_const.LANDING_INDEX_CHILD_COMPANY,
                platform_const.LANDING_INDEX_DEPARTMENT
            )

        positions_data = yield self.get_positions_data(conf_search_seq, company.id)

        if platform_const.LANDING_INDEX_CITY in conf_search_seq:
            positions_data = self.split_cities(positions_data)

        if platform_const.LANDING_INDEX_CHILD_COMPANY in conf_search_seq:
            positions_data = yield self.append_child_company_name(positions_data)

        self.logger.debug(conf_search_seq)

        key_order = [platform_const.LANDING[kn].get("display_key") for kn in conf_search_seq]

        positions_data_values = []
        for e in positions_data:
            to_append = []
            for k in key_order:
                if k == 'child_company_abbr':
                    to_append.append(e.get(k))
                else:
                    to_append.append({"text": e.get(k), "value": e.get(k)})

            positions_data_values.append(to_append)

        dedupped_position_data_values = list_dedup_list(positions_data_values)

        return ObjectDict({
            "field_name": [platform_const.LANDING[e].get("name") for e in conf_search_seq],
            "field_form_name": [platform_const.LANDING[e].get("form_name") for e in conf_search_seq],
            "values": dedupped_position_data_values
        })
