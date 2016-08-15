# coding=utf-8

# Copyright 2016 MoSeeker

import re
from tornado import gen
from tornado.util import ObjectDict
from service.page.base import PageService
from utils.tool.date_tool import jd_update_date
from utils.tool.str_tool import gen_salary

class PositionPageService(PageService):

    @gen.coroutine
    def get_position(self, conds, fields=[]):

        position = {}
        position_res = yield self.job_position_ds.get_position(conds, fields)
        if not position_res:
            raise gen.Return(position)

        update_time = jd_update_date(position_res.get('update_time', ''))

        # 月薪
        salary = gen_salary(position_res.get("salary_top"), position_res.get("salary_bottom"))

        # 福利特色
        feature_array = []
        if position_res.get('feature', ''):
            feature = position_res.get('feature', '').replace("\n", "").replace("\r", "")
            feature_array = re.split(u'#', feature.decode("utf-8"))

        # 职位基础信息拼装
        position = {
            'id': position_res.get('id', ''),
            'title': position_res.get('title', ''),
            'company_id': int(position_res.get('company_id', 0)),
            'department': position_res.get('department', ''),
            # 'status': position_res.get('status', 0),
            'candidate_source': self.constant.CANDIDATE_SOURCE.get(str(position_res.get('candidate_source', 0))),
            'employment_type': self.constant.EMPLOYMENT_TYPE.get(str(position_res.get('employment_type', 0))),
            'update_time': update_time,
            # 'stop_date': position_res.get('stop_date', ''),
            "salary": salary,
            "city": position_res.get('city', ''),
            "occupation": position_res.get('occupation', ''),
            "experience": position_res.get('experience', '')
                          + (self.constant.EXPERIENCE_UNIT if position_res.get('experience', '') else '')
                          + (self.constant.POSITION_ABOVE if position_res.get('experience_above', 0) else ''),
            "language": position_res.get('language', ''),
            "count": int(position_res.get('count', 0)),
            "degree": self.constant.DEGREE.get(str(position_res.get('degree', 0)))
                      + self.constant.POSITION_ABOVE if position_res.get('degree_above', 0) else '',
            "management": position_res.get('management', ''),
            "accountabilities": position_res.get('accountabilities', ''),
            "requirement": position_res.get('requirement', ''),
            "feature": feature_array,
            "overdue": False if position_res.get('status', 0) == 0 else True
        }

        raise gen.Return(position)

    @gen.coroutine
    def get_positions_list(self, conds, fields, options=[], appends=[]):

        """
        获得职位列表
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields, options, appends)
        raise gen.Return(positions_list)

    @gen.coroutine
    def get_positions_cities_list(self, company_id):

        """
        获得公司发布的职位中所有城市列表
        :param company_id:
        :return:
        """

        conds = {
            "company_id": company_id
        }

        fields = ["city"]

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields)
        cities = []
        for item in positions_list:
            cities_tmp = re.split(u'，', item.get("city"))
            for city in cities_tmp:
                if not city:
                    continue
                cities.append(city)
        cities_list = list(set(cities))
        raise gen.Return(cities_list)

    @gen.coroutine
    def get_positions_occupations_list(self, company_id):

        """
        获得公司发布的职位中所有职能列表
        :param company_id:
        :return:
        """

        conds = {
            "company_id": company_id
        }

        fields = ["occupation"]

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields)
        occupations = []
        for item in positions_list:
            if not item.get("occupation"):
                continue
            occupations.append(item.get("occupation"))
        occupations_list = list(set(occupations))
        raise gen.Return(occupations_list)

    @gen.coroutine
    def get_positions_departments_list(self, company_id):

        """
        获得公司发布的职位中所有部门列表
        :param company_id:
        :return:
        """

        conds = {
            "company_id": company_id
        }

        fields = ["department"]

        positions_list = yield self.job_position_ds.get_positions_list(conds, fields)
        departments = []
        for item in positions_list:
            if not item.get("department"):
                continue
            departments.append(item.get("department"))
        departments_list = list(set(departments))
        raise gen.Return(departments_list)