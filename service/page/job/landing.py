# coding=utf-8

# Copyright 2016 MoSeeker

# @Time    : 8/17/16 7:01 PM
# @Author  : Panda
# @File    : landing.py

import re
from tornado import gen
import pypinyin
from pypinyin import pinyin
from service.page.base import PageService

class LandingPageService(PageService):

    @gen.coroutine
    def get_landing_item(self, company, company_id):

        """
        根据HR设置获得搜索页页面栏目排序
        :param search_seq:
        :return:
        """

        res = []
        for item in company.get("conf_search_seq", []):

            result = yield self.get_positions_filter_list(company_id)
            # 工作地点
            index = int(item.get("index"))
            if index == self.plat_constant.LANDING_INDEX_CITY:
                city = {}
                city['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                city['values'] = result.get("cities")
                city['key'] = "city"
                res.append(city)

            # 薪资范围
            elif index == self.plat_constant.LANDING_INDEX_SALARY:
                salary = {}
                salary['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                salary['values'] = [{"value": k, "text": v.get("name")} for k, v in sorted(self.plat_constant.SALARY.items())]
                salary['key'] = "salary"
                res.append(salary)

            # 职位职能
            elif index == self.plat_constant.LANDING_INDEX_OCCUPATION:
                occupation = {}
                occupation['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                occupation['values'] = result.get("occupations")
                occupation['key'] = "occupation"
                res.append(occupation)

            # 所属部门
            elif index == self.plat_constant.LANDING_INDEX_DEPARTMENT:
                department = {}
                department['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                department['values'] = result.get("departments")
                department['key'] = "department"
                res.append(department)

            # 招聘类型
            elif index == self.plat_constant.LANDING_INDEX_CANDIDATE:
                candidate_source = {}
                candidate_source['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                candidate_source['values'] = [{"value": k, "text": v} for k, v in sorted(self.constant.CANDIDATE_SOURCE.items())]
                candidate_source['key'] = "candidate_source"
                res.append(candidate_source)

            # 工作性质
            elif index == self.plat_constant.LANDING_INDEX_EMPLOYMENT:
                employment_type = {}
                employment_type['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                employment_type['values'] = [{"value": k, "text": v} for k, v in sorted(self.constant.EMPLOYMENT_TYPE.items())]
                employment_type['key'] = "employment_type"
                res.append(employment_type)

            # 学历要求
            elif index == self.plat_constant.LANDING_INDEX_DEGREE:
                degree = {}
                degree['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                degree['values'] = [{"value": k, "text": v} for k, v in sorted(self.plat_constant.DEGREE.items())]
                degree['key'] = "degree"
                res.append(degree)

            # 子公司名称
            elif index == self.plat_constant.LANGDING_INDEX_CHILD_COMPANY:
                conds = {
                    "parent_id": company_id,
                    "disable": self.constant.STATUS_INUSE
                }
                fields = ["id", "abbreviation"]
                child_company_res = yield self.hr_company_ds.get_companys_list(conds, fields)

                # 添加母公司信息
                child_company_values = [{
                    "id": company_id,
                    "abbreviation": company.get("abbreviation")
                }]

                child_company = {}
                child_company['values'] = child_company_values + list(child_company_res)
                child_company['name'] = self.plat_constant.LANDING.get(index).get("chpe")
                child_company['key'] = "did"
                res.append(child_company)

            # 企业自定义字段，并且配置了企业自定义字段标题
            elif index == self.plat_constant.LANDING_INDEX_CUSTOM and company.get("conf_job_custom_title"):
                conds = {
                    "company_id": company_id,
                    "status": self.constant.STATUS_INUSE
                }
                fields = ['name']

                custom = {}
                custom['name'] = company.get("conf_job_custom_title")
                custom['values'] = yield self.get_customs_list(conds, fields)
                custom['key'] = "custom"
                res.append(custom)

        raise gen.Return(res)

    @gen.coroutine
    def get_positions_filter_list(self, company_id):

        """
        获得公司发布的职位中所有城市列表，职能列表，部门列表，
        :param company_id:
        :return:
        """

        conds = {
            "company_id": company_id,
            "status": 0,
        }

        fields = ["city", "occupation", "department"]

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields)
        cities = {}
        occupations = []
        departments = []
        for item in positions_list:
            cities_tmp = re.split(u'，', item.get("city"))
            for city in cities_tmp:
                if not city:
                    continue
                self.logger.debug("pinyin: %s" % pinyin(city, style=pypinyin.FIRST_LETTER))
                cities[city] = pinyin(city, style=pypinyin.FIRST_LETTER)[0].upper()

            if item.get("occupation") and not item.get("occupation") in occupations:
                occupations.append(item.get("occupation"))

            if item.get("department") and not item.get("department") in departments:
                departments.append(item.get("department"))

        # 根据拼音首字母排序
        cities = sorted(cities.items(), key = lambda x:x[1])

        res = {
            "cities": cities.keys(),
            "occupations": occupations,
            "departments": departments,
        }
        raise gen.Return(res)

    @gen.coroutine
    def get_customs_list(self, conds, fields, options=[], appends=[]):

        """
        获得职位自定义字段
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        customs_list_res = yield self.job_custom_ds.get_customs_list(conds, fields, options, appends)
        customs_list = [item.get("name") for item in customs_list_res]
        raise gen.Return(customs_list)
