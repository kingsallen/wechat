# coding=utf-8

# @Time    : 4/18/17 11:57
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

from tornado import gen
import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.str_tool import split, gen_salary
from util.tool.url_tool import make_static_url

class AggregationPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def get_aggregation_banner(self):

        """
        获得聚合号列表页 banner 头图
        :return:
        """

        # banner_res = yield self.thrift_position_ds.get_aggregation_banner()
        # raise gen.Return(banner_res)
        pass

    @gen.coroutine
    def opt_es(self, salary_top, salary_bottom, salary_negotiable, keywords, city, industry, page_no, page_size):

        params = ObjectDict({
            "salary_top": salary_top,
            "salary_bottom": salary_bottom,
            "salary_negotiable": salary_negotiable,
            "keywords": keywords,
            "city": city,
            "industry": industry
        })

        page_from = page_no * page_size
        if page_no == 0:
            # 如果是首页，则取300条数据，热招企业需要
            page_size = 300

        es_res = yield self.es_ds.get_es_position(params, page_from, page_size)
        return es_res

    def opt_agg_positions(self, es_res, page_size):

        """
        处理搜索职位结果
        :param es_res:
        :return:
        """

        hot_positons = list()
        if es_res.hits:
            for item in es_res.hits.hits:
                agg_position = ObjectDict()
                agg_position["id"] = item.get("_source").get("position").get("id")
                agg_position["title"] = item.get("_source").get("position").get("title")
                agg_position["salary"] = gen_salary(item.get("_source").get("position").get("salary_top"), item.get("_source").get("position").get("salary_bottom"))
                agg_position["team"] = item.get("_source").get("team", {}).get("name","")

                agg_position["degree"] = const.DEGREE.get(str(int(item.get("_source").get("position").get("degree")))) \
                                         + (const.POSITION_ABOVE if item.get("_source").get("position").get("degree_above") else '')
                agg_position["experience"] = item.get("_source").get("position").get("experience") \
                                             + (const.EXPERIENCE_UNIT if item.get("_source").get("position").get("experience") else '') \
                                             + (const.POSITION_ABOVE if item.get("_source").get("position").get("experience_above") else '')
                agg_position["has_team"] = True if item.get("_source").get("team", {}) else False
                agg_position["team_img"] = item.get("_source").get("position").get("title")
                agg_position["job_img"] = item.get("_source").get("position").get("title")
                agg_position["company_img"] = item.get("_source").get("position").get("title")

                agg_position["resources"] = item.get("_source").get("position").get("title")

                hot_positons.append(agg_position)
                if len(hot_positons) == page_size:
                    break

        return hot_positons

    def opt_agg_company(self, es_res):

        """
        处理热招企业，包括企业信息，搜索结果中的城市合集，在招企业职位数
        :param es_res:
        :return:
        """

        results = ObjectDict()
        if es_res.hits:
            for item in es_res.hits.hits:
                if item.get("_source").get("position").get("status") != 0:
                    continue
                city_list = split(item.get("_source").get("position").get("city"), ['，', ',']) \
                    if item.get("_source").get("position").get("city") else list()
                company_id_str = str(item.get("_source").get("company").get("id"))
                if results.get(company_id_str):
                    if city_list:
                        city_rep = results[company_id_str].get("city") + city_list
                        results[company_id_str].city = city_rep

                    results[company_id_str].position_cnt += 1

                else:
                    results[company_id_str] = ObjectDict({
                        "company": item.get("_source").get("company"),
                        "city": city_list,
                        "position_cnt": 1,
                    })

            for key, value in results.items():
                city = ObjectDict()
                for i in value.city:
                    if value.city.count(i) > 0:
                        city[i] = value.city.count(i)
                city = sorted(city.items(), key=lambda x:x[1], reverse=True)
                value.city = [item[0] for item in city[:5]]

        hot_company = list()
        for item in results.values():
            agg_company = ObjectDict()
            agg_company["id"] = item.company.id
            agg_company["logo"] = make_static_url(item.company.logo or const.COMPANY_HEADIMG)
            agg_company["abbreviation"] = item.company.abbreviation
            agg_company["position_count"] = item.position_cnt
            agg_company["city"] = item.city
            hot_company.append(agg_company)

        return hot_company
