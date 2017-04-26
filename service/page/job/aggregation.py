# coding=utf-8

# @Time    : 4/18/17 11:57
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

import ujson
from tornado import gen
import conf.common as const
import conf.qx as qx_const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.str_tool import split, gen_salary, gen_degree, gen_experience
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

        ret = yield self.thrift_position_ds.get_aggregation_banner()
        banner = ObjectDict()
        if ret.data:
            banner = ObjectDict({
                "image_url": make_static_url(ret.data.imageUrl),
                "href_url": ret.data.hrefUrl
            })

        raise gen.Return(banner)

    @gen.coroutine
    def get_user_position_status(self, user_id, position_ids):
        """
        批量查询用户职位状态：已阅，已收藏，已投递
        :param user_id:
        :param position_ids:
        :return:
        """

        ret = yield self.thrift_searchcondition_ds.get_user_position_status(user_id, position_ids)
        banner = ObjectDict()
        if ret.positionStatus:
            self.logger.debug("get_user_position_status:{}".format(ret.positionStatus))

        raise gen.Return(banner)

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
            # page_size = 300
            page_size = 10

        es_res = yield self.es_ds.get_es_position(params, page_from, page_size)
        return es_res

    @gen.coroutine
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
                agg_position["degree"] = gen_degree(int(item.get("_source").get("position").get("degree")), item.get("_source").get("position").get("degree_above"))
                agg_position["experience"] = gen_experience(item.get("_source").get("position").get("experience"), item.get("_source").get("position").get("experience_above"))
                agg_position["has_team"] = True if item.get("_source").get("team", {}) else False

                team_img, job_img, company_img = yield self.opt_jd_home_img(item.get("_source").get("company",{}).get("industry"), item)
                agg_position["team_img"] = make_static_url(team_img)
                agg_position["job_img"] = make_static_url(job_img)
                agg_position["company_img"] = make_static_url(company_img)
                agg_position["resources"] = item.get("_source").get("position").get("title")

                hot_positons.append(agg_position)
                if len(hot_positons) == page_size:
                    break

        return hot_positons

    @gen.coroutine
    def opt_jd_home_img(self, industry, item):

        industries = yield self.infra_dict_ds.get_industries()
        self.logger.debug("industries:{}".format(industries))
        indus_dict = ObjectDict()
        for param in industries:
            for indus in param.get("list"):
                indus_dict[indus.get("name")] = indus

        if industry:
            indus_parent_code = int(indus_dict.get(industry).get("code")/100) * 100
        else:
            indus_parent_code = ""

        if not item.get("_source").get("team",{}).get("resource"):
            team_img = qx_const.JD_BACKGROUND_IMG.get(indus_parent_code).get("team_img")
        else:
            team_img = item.get("_source").get("team",{}).get("resource",{}).get("res_url")

        if not item.get("_source").get("jd_pic",{}).get("position_pic",{}).get("first_pic",{}):
            job_img = qx_const.JD_BACKGROUND_IMG.get(indus_parent_code).get("job_img")
        else:
            job_img = item.get("_source").get("jd_pic",{}).get("position_pic",{}).get("first_pic",{}).get("res_url")

        if not item.get("_source").get("company",{}).get("impression",{}):
            company_img = qx_const.JD_BACKGROUND_IMG.get(indus_parent_code).get("company_img")
        else:
            impression = ujson.loads(item.get("_source").get("company",{}).get("impression",{}))
            company_img = impression.get("impression0")

        return team_img, job_img, company_img

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

    # def _gen_resources(self, jd_pic):

