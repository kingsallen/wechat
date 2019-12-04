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
    def get_positions_data(self, conf_search_seq, company_id, search_condition_dict, salary_dict, display_locale, is_referral):
        """ 从 ES 获取全部职位信息
        可以正确解析 salary
        """
        ret = []

        res = yield self.infra_position_ds.get_es_positions(ObjectDict({
            "company_id": company_id,
            "query_size": platform_const.LANDING_QUERY_SIZE,
            "referral": bool(is_referral),
            "salary_bottom": salary_dict.get("salary_bottom"),
            "salary_top": salary_dict.get("salary_top"),
            "search_condition": search_condition_dict
        }))
        result_list = res.data
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
            source = ObjectDict(self.sub_nested_dict(source, key_list))

            if 'salary_top' in key_list:
                # 对 salary 做特殊处理 (salary_top, salary_bottom) -> salary
                salary = [
                    v.get("name") for v in platform_const.SALARY.values()
                    if v.salary_bottom == source.get("salary_bottom") and
                    v.salary_top == source.get("salary_top")
                    ]

                source.salary = salary[0] if salary else ''
                source.pop("salary_top", None)
                source.pop("salary_bottom", None)

            ret.append(source)

        return ret

    def sub_nested_dict(self, somedict, somekeys):
        if isinstance(somekeys, list):
            ret = {}
            for key in somekeys:
                es_key = self.get_by_value_dict(key, platform_const.LANDING)
                value = somedict.get(es_key.split(".")[0])
                if value:
                    if key in ["city", "city_ename"]:
                        citys = []
                        for city in value:
                            citys.append(city.get(es_key.split(".")[1]))
                        ret.update({key: citys})
                    elif key == "position_type":
                        ret.update({key: 0 if value.get(es_key.split(".")[1]) is None else value.get(es_key.split(".")[1])}) # position_type是新增属性，老数据没有这个属性
                    else:
                        ret.update({key: value.get(es_key.split(".")[1])})
                else:
                    ret.update({key: ""})
            # ret = {k: somedict.get(k, default) for k in somekeys}
        elif isinstance(somekeys, str):
            key = somekeys
            es_key = self.get_by_value_dict(key, platform_const.LANDING)
            value = somedict.get(es_key.split(".")[0])
            if value:
                if key == "position_type":
                    ret = {key: 0 if value.get(es_key.split(".")[1]) is None else value.get(es_key.split(".")[1])}
                else:
                    ret = {key: value.get(es_key.split(".")[1])}
            else:
                ret = {key: ""}
        else:
            raise ValueError('sub dict key should be list or str')
        return ObjectDict(ret)

    @staticmethod
    def get_by_value_dict(value, nested_dict):
        if value == "salary_top":
            return nested_dict[2]["es_key"][0]
        elif value == "salary_bottom":
            return nested_dict[2]["es_key"][1]
        elif value == "city_ename":
            return "citys.ename"
        else:
            for key_out, value_out in nested_dict.items():
                for key_in, value_in in value_out.items():
                    if value_in == value:
                        return value_out["es_key"]
            return ""

    @staticmethod
    def split_cities(data, *, display_locale=None):
        """如果一条数据中包含多个城市，应该分裂成多条数据"""
        ret = []
        if display_locale == "en_US":
            key_to_split = 'city_ename'
        else:
            key_to_split = 'city'

        for e in data:
            e = ObjectDict(e)
            value_to_split = e.get(key_to_split)
            if value_to_split:
                for item in value_to_split:
                    new_e = e.copy()
                    new_e[key_to_split] = item
                    ret.append(ObjectDict(new_e))
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
        :param display_locale: 国际化的语言
        :param locale: 国际化对象
        :param params: neoweixinrefer请求链接上的参数
        :param company: 公司信息
        :param is_referral: 是否内推
        :return: {"field_name": ['地点', '子公司', '部门'],
                  "field_form_name": ['city', '...', 'team_name']
                  "values": [[{"text": '上海', "value": "上海"}, ...],
                             [...],
                             ...]
                 }
        """
        conf_search_seq = tuple([int(e.index) for e in company.get("conf_search_seq")])

        # 获取链接上配置的筛选参数
        display_key_dict = dict()
        all_form_name = [platform_const.LANDING[e].get('form_name') for e in range(1, 11)]
        for key, value in params.items():
            if value and key in all_form_name:
                display_key_dict[key] = value
        self.logger.debug(display_key_dict)
        search_params = ObjectDict({
            "conf_search_seq": conf_search_seq,
            "company_id": company.get("id"),
            "display_locale": display_locale,
            "referral": is_referral,
            "params": display_key_dict
        })
        data = yield self.infra_position_ds.get_es_position_list(search_params)

        # 国际化
        field_form_name = data.field_form_name
        positions = data.get("values")  # 不要使用data.values，这是dict的built_in method
        conf_search_seq_plus = data.conf_search_index_plus
        for index, k in enumerate(field_form_name):
            for e in positions:
                if len(e) > index and e[index] and e[index].get("text"):  # 理论上，这个数据一定是有的，但是防止基础服务的数据有问题，还是加上判断
                    if k == 'candidate_source':
                        text = locale.translate(const.CANDIDATE_SOURCE_SEARCH_LOCALE.get(e[index].get("text")))
                        e[index].update({"text": text})
                    elif k == 'employment_type':
                        text = locale.translate(const.EMPLOYMENT_TYPE_SEARCH_LOCALE.get(e[index].get("text")))
                        e[index].update({"text": text})
                    elif k == 'degree':
                        content = e[index].get("text")
                        if "及以上" in content:
                            content = content.rstrip("及以上")
                            text = locale.translate(const.DEGREE_SEARCH_LOCALE.get(content))
                        else:
                            text = locale.translate(const.DEGREE_SEARCH_LOCALE.get(content))
                        e[index].update({"text": text})
                    elif k == 'position_type':
                        text = locale.translate(const.POSITION_TYPE_LOCALE.get(e[index].get("text")))
                        e[index].update({"text": text})
        self.logger.debug("高级筛选项国际化, positions:{}".format(positions))

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
            "field_form_name": field_form_name,
            "values": positions
        })
