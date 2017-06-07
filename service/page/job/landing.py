# coding=utf-8


import json

from tornado import gen, httpclient

from service.page.base import PageService
from util.common import ObjectDict
from util.tool.str_tool import to_str
from util.tool.dict_tool import sub_dict
from util.tool.str_tool import split, set_literl
from setting import settings
import conf.platform as platform_const




class LandingPageService(PageService):
    def __init__(self):
        super().__init__()


    def make_key_list(self, conf_search_seq):
        """ 根据 conf_search_seq 来生成 key list
        :param conf_search_seq: 
        :return: key_list
        """
        key_list = ["id"]

        for key in conf_search_seq:
            to_append = platform_const.LANDING.get(key)
            if to_append:
                to_append = to_append.key
                if isinstance(to_append, list):
                    key_list = key_list + to_append
                else:
                    key_list.append(to_append)
        self.logger.debug("key_list: %s" % key_list)
        return key_list

    @gen.coroutine
    def get_positions_data(self, conf_search_seq, company_id=39978):
        """ 从 ES 获取全部职位信息
        可以正确解析 salary
        """
        ret = []
        query_size = 5000

        url = settings.es + "/index/_search?company_id:%s+AND+status:0&size:%s" % (company_id, query_size)
        response = yield httpclient.AsyncHTTPClient().fetch(url)

        body = ObjectDict(json.loads(to_str(response.body)))
        result_list = body.hits.hits

        # 获取筛选项
        key_list = self.make_key_list(conf_search_seq)

        for e in result_list:
            source = e.get("_source")

            # 使用 key_list 来筛选 source
            source = ObjectDict(sub_dict(source, key_list))

            print(source)
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

    def split_cities(self, data, delimiter=None):
        """如果一条数据中包含多个城市，应该分裂成多条数据"""
        ret = []
        key_to_split = 'city'
        if not delimiter:
            delimiter = [",", "，"]

        for e in data:
            value_to_split = e.get(key_to_split)
            if value_to_split:
                splitted_items = split(value_to_split, delimiter)
                if len(splitted_items) > 1:
                    for item in splitted_items:
                        new_e = e.copy()
                        new_e[key_to_split] = item
                        ret.append(new_e)
                else:
                    ret.append(e)
            else:
                ret.append(e)
        return ret

    @gen.coroutine
    def append_child_company_name_to(self, data):
        child_company_ids = [v.publisher_company_id for v in data]

        child_company_id_abbr_list = yield self.hr_company_ds.get_companys_list(
            conds="id in " + set_literl(child_company_ids),
            fields=["id", "abbreviation"]
        )
        child_company_id_abbr_dict = {e.id:e.abbreviation for e in child_company_id_abbr_list}

        for d in data:
            if d.publisher_company_id:
                d.child_company_abbr = child_company_id_abbr_dict.get(d.publisher_company_id, "")
            else:
                d.child_company_abbr = ""

        return data

    @gen.coroutine
    def make_search_seq(self, company):
        """
        生成高级搜索功能中前端需要的数据
        :param company:
        :return: {"field_name": ['地点', '子公司', '部门'],
                  "values": [['上海', '寻仟', '研发部'],
                             ['上海', '寻仟', '设计部'],
                             ...]
                 }
        """
        conf_search_seq = company.get(
            "conf_search_seq",
            (
                platform_const.LANDING_INDEX_CITY,
                platform_const.LANDING_INDEX_SALARY,
                platform_const.LANDING_INDEX_CHILD_COMPANY,
                platform_const.LANDING_INDEX_DEPARTMENT
            )
        )

        positions_data = yield self.get_positions_data(conf_search_seq, company.id)
        positions_data = self.split_cities(positions_data)

        if platform_const.LANDING_INDEX_CHILD_COMPANY in conf_search_seq:
            positions_data = yield self.append_child_company_name(positions_data)

        return ObjectDict({
            "field_name": [platform_const.LANDING[e].get("name") for e in conf_search_seq],
            "values": positions_data
        })

    # @gen.coroutine
    # def get_landing_item(self, company, company_id, selected):
    #
    #     """
    #     根据HR设置获得搜索页页面栏目排序
    #     :param company:
    #     :param company_id:
    #     :param selected
    #     :return:
    #     """
    #
    #     res = []
    #     for item in company.get("conf_search_seq", []):
    #
    #         result = yield self.get_positions_filter_list(company_id)
    #         # 工作地点
    #         index = int(item.get("index"))
    #         if index == self.plat_constant.LANDING_INDEX_CITY:
    #             city = {}
    #             city['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #             city['values'] = result.get("cities")
    #             city['key'] = "city"
    #             city['selected'] = selected.get("city")
    #             res.append(city)
    #
    #         # 薪资范围
    #         elif index == self.plat_constant.LANDING_INDEX_SALARY:
    #             salary = {}
    #             salary['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #             salary['values'] = [{"value": k, "text": v.get("name")} for k, v in
    #                                 sorted(self.plat_constant.SALARY.items())]
    #             salary['key'] = "salary"
    #             salary['selected'] = selected.get("salary")
    #             res.append(salary)
    #
    #         # 职位职能
    #         elif index == self.plat_constant.LANDING_INDEX_OCCUPATION:
    #             occupation = {}
    #             if company.conf_job_occupation:
    #                 occupation['name'] = company.conf_job_occupation
    #             else:
    #                 occupation['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #
    #             occupation['values'] = result.get("occupations")
    #             occupation['key'] = "occupation"
    #             occupation['selected'] = selected.get("occupation")
    #             res.append(occupation)
    #
    #         # 所属部门
    #         elif index == self.plat_constant.LANDING_INDEX_DEPARTMENT:
    #             enabled_departments = yield self.hr_team_ds.get_team_list(
    #                 conds={"disable": 0, "company_id": company_id}, fields=["id", "name"])
    #             department = {}
    #             department['name'] = company.conf_teamname_custom.get("teamname_custom", "")
    #             department['values'] = [dep.get("name", "") for dep in enabled_departments]
    #             department['key'] = "team_name"
    #             department['selected'] = selected.get("team_name")
    #             res.append(department)
    #
    #         # 招聘类型
    #         elif index == self.plat_constant.LANDING_INDEX_CANDIDATE:
    #             candidate_source = {}
    #             candidate_source['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #             candidate_source['values'] = [{"value": k, "text": v} for k, v in
    #                                           sorted(self.constant.CANDIDATE_SOURCE.items())]
    #             candidate_source['key'] = "candidate_source"
    #             candidate_source['selected'] = selected.get("candidate_source")
    #             res.append(candidate_source)
    #
    #         # 工作性质
    #         elif index == self.plat_constant.LANDING_INDEX_EMPLOYMENT:
    #             employment_type = {}
    #             employment_type['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #             employment_type['values'] = [{"value": k, "text": v} for k, v in
    #                                          sorted(self.constant.EMPLOYMENT_TYPE.items())]
    #             employment_type['key'] = "employment_type"
    #             employment_type['selected'] = selected.get("employment_type")
    #             res.append(employment_type)
    #
    #         # 学历要求
    #         elif index == self.plat_constant.LANDING_INDEX_DEGREE:
    #             degree = {}
    #             degree['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #             degree['values'] = [{"value": k, "text": v} for k, v in sorted(self.plat_constant.DEGREE.items())]
    #             degree['key'] = "degree"
    #             degree['selected'] = selected.get("degree")
    #             res.append(degree)
    #
    #         # 子公司名称
    #         elif index == self.plat_constant.LANDING_INDEX_CHILD_COMPANY:
    #             conds = {
    #                 "parent_id": company_id,
    #                 "disable": self.constant.STATUS_INUSE
    #             }
    #             fields = ["id", "abbreviation"]
    #             child_company_res = yield self.hr_company_ds.get_companys_list(conds, fields)
    #
    #             # 添加母公司信息
    #             child_company_values = [{
    #                 "id": company_id,
    #                 "abbreviation": company.get("abbreviation")
    #             }]
    #
    #             child_company = {}
    #             child_company['values'] = child_company_values + list(child_company_res)
    #             child_company['name'] = self.plat_constant.LANDING.get(index).get("chpe")
    #             child_company['key'] = "did"
    #             child_company['selected'] = selected.get("did")
    #             res.append(child_company)
    #
    #         # 企业自定义字段，并且配置了企业自定义字段标题
    #         elif index == self.plat_constant.LANDING_INDEX_CUSTOM and company.get("conf_job_custom_title"):
    #             conds = {
    #                 "company_id": company_id,
    #                 "status": self.constant.STATUS_INUSE
    #             }
    #             fields = ['name']
    #
    #             custom = {}
    #             custom['name'] = company.get("conf_job_custom_title")
    #             custom['values'] = yield self.get_customs_list(conds, fields)
    #             custom['key'] = "custom"
    #             custom['selected'] = selected.get("custom")
    #             res.append(custom)
    #
    #     raise gen.Return(res)

    # @gen.coroutine
    # def get_positions_filter_list(self, company_id):
    #     """
    #     获得公司发布的职位中所有城市列表，，部门列表，职能列表
    #     :param company_id:
    #     :return:
    #     """
    #
    #     conds = {
    #         "company_id": company_id,
    #         "status": 0,
    #     }
    #
    #     fields = ["id", "city", "occupation", "department"]
    #
    #     positions_list = yield self.job_position_ds.get_positions_list(conds, fields)
    #     cities = {}
    #     occupations = yield self.get_occupations(positions_list)
    #     departments = []
    #     for item in positions_list:
    #         cities_tmp = split(item.get("city"), ['，', ','])
    #         for city in cities_tmp:
    #             if not city:
    #                 continue
    #             cities[city] = lazy_pinyin(city)[0].upper()
    #
    #         if item.get("department"):
    #             departments_tmp = split(item.get("department"), ['，', ','])
    #             for department in departments_tmp:
    #                 if not department or item.get("department") in departments:
    #                     continue
    #                 departments.append(department)
    #
    #     # 根据拼音首字母排序
    #     cities = sorted(cities.items(), key=lambda x: x[1])
    #     cities = [city[0] for city in cities]
    #
    #     res = {
    #         "cities": cities,
    #         "occupations": occupations,
    #         "departments": departments,
    #     }
    #     raise gen.Return(res)

    # @gen.coroutine
    # def get_customs_list(self, conds, fields, options=[], appends=[]):
    #     """
    #     获得职位自定义字段
    #     :param conds:
    #     :param fields:
    #     :param options:
    #     :param appends:
    #     :return:
    #     """
    #
    #     customs_list_res = yield self.job_custom_ds.get_customs_list(conds, fields, options, appends)
    #     customs_list = [item.get("name") for item in customs_list_res]
    #     raise gen.Return(customs_list)

    # @gen.coroutine
    # def get_occupations(self, positions):
    #     """
    #     获取职位对应的occupations
    #     :param positions:
    #     :return:
    #     """
    #     if not positions:
    #         return []
    #
    #     # 根据pid查job_occupation_id
    #     position_ids = [p.id for p in positions]
    #     position_exts = yield self.job_position_ext_ds.get_position_ext_list(
    #         conds="pid in %s" % set_literl(position_ids),
    #         fields=["pid", "job_occupation_id"])
    #     position_exts_job_occupation_ids = list(set([p_ext["job_occupation_id"] for p_ext in position_exts]))
    #
    #     # 根据job_occupation_id获得job_occupation的名字
    #     if not position_exts_job_occupation_ids:
    #         occupations = []
    #     else:
    #         job_occupations = yield self.job_occupation_ds.get_occupations_list(
    #             conds={"status": self.constant.STATUS_INUSE},
    #             fields=["id", "name"],
    #             appends=["and id in %s" % set_literl(position_exts_job_occupation_ids)])
    #         occupations = [jo.name for jo in job_occupations]
    #     return occupations
