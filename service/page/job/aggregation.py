# coding=utf-8

# @Time    : 4/18/17 11:57
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

import random
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
    def opt_es(self, salary_top, salary_bottom, salary_negotiable, keywords, city, industry, page_no):
        """
        拼接 ES 搜索职位
        :param salary_top:
        :param salary_bottom:
        :param salary_negotiable:
        :param keywords:
        :param city:
        :param industry:
        :param page_no:
        :param page_size:
        :return:
        """

        # 查询范围 1-30页
        if page_no < 0 or page_no > 30:
            return ObjectDict()

        # 处理 salley_top, salley_bottom
        salary_top = int(int(salary_top)/1000) if salary_top else None
        salary_bottom = int(int(salary_bottom)/1000) if salary_bottom else None

        # 如果 salary_top,salary_bottom都为30k，那么salary_top转为999.数据库中上限为999
        if salary_top and salary_bottom \
            and salary_top >=30 and salary_bottom >= 30:
            salary_top = 999

        params = ObjectDict({
            "salary_top": salary_top,
            "salary_bottom": salary_bottom,
            "salary_negotiable": salary_negotiable,
            "keywords": keywords,
            "city": city,
            "industry": industry
        })

        # 由于需要按人工设置的 weight进行排序，es 不支持先按关键词搜索，再按 weight 排序
        # 因此由 python 实现排序，并分页
        es_res = yield self.es_ds.get_es_positions(params, 0, 300)
        if es_res.hits.hits:
            es_res = sorted(es_res.hits.hits, key=lambda x:x.get("_source").get("weight"), reverse = True)

        return es_res

    @gen.coroutine
    def opt_es_position(self, position_id):
        """
        搜索职位
        :param position_id:
        :return:
        """

        es_res = yield self.es_ds.get_es_position(position_id)
        return es_res

    @gen.coroutine
    def opt_agg_positions(self, es_res, page_no, page_size, user_id, city):

        """
        处理搜索职位结果
        :param es_res:
        :param page_from:
        :param page_size:
        :param user_id:
        :param city: 如果用户在搜索条件里面输入了选择的城市，那么不管该职位实际在哪些城市发布，在显示在列表页的时候，只显示用户选择的地址
        :return:
        """

        city_list = split(city, [","]) if city else list()

        page_from = (page_no - 1) * page_size
        page_block = page_no * page_size

        self.logger.debug("page_from:{}".format(page_from))
        self.logger.debug("page_block:{}".format(page_block))

        hot_positons = ObjectDict()
        if es_res:
            es_res = es_res[page_from:page_block]
            self.logger.debug("es_res 3:{}".format(es_res))
            for item in es_res:
                self.logger.debug("1111111111:{}".format(item.get("_source").get("weight")))
                self.logger.debug("1111111111:{}".format(item.get("_source").get("position").get("id")))
                self.logger.debug("1111111111:{}".format(item.get("_source").get("position").get("title")))
                id = int(item.get("_source").get("position").get("id"))
                team_img, job_img, company_img = yield self.opt_jd_home_img(item)

                company = ObjectDict({
                    "id": item.get("_source").get("company", {}).get("id"),
                    "logo": make_static_url(item.get("_source").get("company", {}).get("logo") or const.COMPANY_HEADIMG),
                    "abbreviation": item.get("_source").get("company", {}).get("abbreviation"),
                })

                # 求搜索 city 和结果 city 的交集
                city_ori = split(item.get("_source").get("position").get("city"), ['，', ','])
                if city_list:
                    city = [c for c in city_ori if c in city_list]
                else:
                    city = city_ori

                hot_positons[id] = ObjectDict({
                    "id": item.get("_source").get("position").get("id"),
                    "title": item.get("_source").get("position").get("title"),
                    "salary": gen_salary(item.get("_source").get("position").get("salary_top"), item.get("_source").get("position").get("salary_bottom")),
                    "team": item.get("_source").get("team", {}).get("name",""),
                    "degree": gen_degree(int(item.get("_source").get("position").get("degree")), item.get("_source").get("position").get("degree_above")),
                    "experience":  gen_experience(item.get("_source").get("position").get("experience"), item.get("_source").get("position").get("experience_above")),
                    "has_team": True if item.get("_source").get("team", {}) else False,
                    "team_img": team_img,
                    "job_img": job_img,
                    "company_img": company_img,
                    "resources": self._gen_resources(item.get("_source").get("jd_pic",{}), item.get("_source").get("company",{})),
                    "user_status": 0,
                    "city": city,
                    "company": company,
                })

        # 处理 0: 未阅，1：已阅，2：已收藏，3：已投递
        positions = yield self._opt_user_positions_status(hot_positons, user_id)
        return list(positions.values())

    @gen.coroutine
    def opt_jd_home_img(self, item):
        """
        处理JD首页行业默认图
        :param item:
        :return:
        """

        industry_type = 0
        if item.get("_source", {}).get("company", {}).get("industry_type", None):
            industry_type = item.get("_source", {}).get("company", {}).get("industry_type")

        team_img = qx_const.JD_BACKGROUND_IMG.get(industry_type).get("team_img")
        job_img = qx_const.JD_BACKGROUND_IMG.get(industry_type).get("job_img")
        company_img = qx_const.JD_BACKGROUND_IMG.get(industry_type).get("company_img")

        if item.get("_source", {}).get("team",{}).get("resource", {}) \
            and item.get("_source", {}).get("team",{}).get("resource", {}).get("res_type", 0) == 0:
            team_img = item.get("_source").get("team",{}).get("resource",{}).get("res_url")

        if item.get("_source", {}).get("jd_pic",{}).get("position_pic",{}).get("first_pic",{}):
            job_img = item.get("_source").get("jd_pic",{}).get("position_pic",{}).get("first_pic",{}).get("res_url")

        if item.get("_source", {}).get("jd_pic",{}).get("company_pic",{}).get("first_pic",{}):
            company_img = item.get("_source").get("jd_pic",{}).get("company_pic",{}).get("first_pic",{}).get("res_url")

        return make_static_url(team_img), make_static_url(job_img), make_static_url(company_img)

    @gen.coroutine
    def opt_agg_company(self, es_res):

        """
        处理热招企业，包括企业信息，搜索结果中的城市合集，在招企业职位数
        :param es_res:
        :return:
        """

        results = ObjectDict()
        if es_res:
            for item in es_res:
                if item.get("_source").get("position").get("status") != 0 \
                    or not item.get("_source").get("company").get("logo") \
                    or not item.get("_source").get("company").get("banner"):
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
                        "weight": 0,
                    })

            for key, value in results.items():
                city = ObjectDict()
                for i in value.city:
                    if value.city.count(i) > 0:
                        city[i] = value.city.count(i)
                city = sorted(city.items(), key=lambda x:x[1], reverse=True)
                value.city = [item[0] for item in city[:5]]

        hot_company = list()
        if not results:
            return hot_company

        # 获得运营推荐公司排在前面
        recommend_company = yield self.campaign_recommend_company_ds.get_campaign_recommend_company(conds={"disable": 0})

        for r_comp in recommend_company:
            comp_id = str(r_comp.get("company_id"))
            if results.get(comp_id):
                results[comp_id].weight = r_comp.get("weight")

        results_cmp = sorted(results.items(), key=lambda d:d[1].get('weight',0), reverse = True)

        for item in results_cmp:
            agg_company = ObjectDict()
            agg_company["id"] = item[1].company.id
            agg_company["logo"] = make_static_url(item[1].company.logo or const.COMPANY_HEADIMG)
            banner = ujson.loads(item[1].company.banner).get("banner0") if item[1].company.banner else ""
            agg_company["banner"] = make_static_url(banner)
            agg_company["abbreviation"] = item[1].company.abbreviation
            agg_company["position_count"] = item[1].position_cnt
            agg_company["city"] = item[1].city
            hot_company.append(agg_company)

        return hot_company[:9]

    def _gen_resources(self, jd_pic, company):

        """
        处理图片逻辑
        :param jd_pic:
        :param company_type:
        :return:
        """

        pic_list = list()
        if jd_pic.get("position_pic"):
            pic_list += jd_pic.get("position_pic").get("other_pic")
        if jd_pic.get("team_pic"):
            pic_list += jd_pic.get("team_pic").get("other_pic")
        if company.get("impression"):
            pic_list += [ObjectDict(res_type=0, res_url=item) for item in ujson.decode(company.get("impression")).values()]
        if company.get("banner"):
            pic_list += [ObjectDict(res_type=0, res_url=item) for item in ujson.decode(company.get("banner")).values()]

        res_resource = list()
        if company.get("type", None) != 0 or len(pic_list) == 0:
            return res_resource

        if len(pic_list) > 3:
            res_resource = random.sample(pic_list, 3)
        else:
            res_resource = pic_list

        for item in res_resource:
            item["type"] = item["res_type"]
            item["url"] = make_static_url(item['res_url'])
            item.pop("cover", None)
            item.pop("res_type", None)
            item.pop("res_url", None)
            item.pop("title", None)

        return res_resource

    @gen.coroutine
    def _opt_user_positions_status(self, hot_positons, user_id):
        """
        处理 0: 未阅，1：已阅，2：已收藏，3：已投递
        :param hot_positons:
        :param user_id:
        :return:
        """

        if not user_id or not hot_positons:
            return hot_positons

        position_ids = hot_positons.keys()
        ret = yield self.thrift_searchcondition_ds.get_user_position_status(user_id, position_ids)
        if ret.positionStatus:
            for key, value in hot_positons.items():
                value["user_status"] = ret.positionStatus.get(key)

        return hot_positons
