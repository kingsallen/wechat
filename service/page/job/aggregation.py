# coding=utf-8

import random
import ujson

from tornado import gen

import conf.common as const
import conf.qx as qx_const
from service.page.base import PageService
from util.common import ObjectDict
from util.tool.str_tool import split, gen_salary, gen_degree_v2, gen_experience_v2
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
    def opt_es(self, salary_top, salary_bottom, salary_negotiable, keywords, city, industry, did, page_from=0, page_size=10):
        """ 拼接 ES 搜索职位
        :param salary_top:
        :param salary_bottom:
        :param salary_negotiable:
        :param keywords:
        :param city:
        :param industry:
        :param did:
        :param page_from:
        :param page_size:
        :return:
        """

        # 处理 salley_top, salley_bottom
        salary_top = int(int(salary_top)/1000) if salary_top else None
        salary_bottom = int(int(salary_bottom)/1000) if salary_bottom else None

        # 如果 salary_top,salary_bottom都为30k，那么salary_top转为999.数据库中上限为999
        if salary_top and salary_bottom \
            and salary_top >=30 and salary_bottom >= 30:
            salary_top = 999

        # 对关键字中的特殊字符做处理
        ignore_str = ['/', 'OR', 'AND', '(', ')', '+', '\\', '（', '）', '-', '&', '–', '|', '|', '[', ']', '!', '{',
                      '}', '^', '\"', '~', '*', '?', ':', '\'', '@', '%', '#', '=', '_', ',']
        for i in ignore_str:
            if i in keywords:
                keywords = keywords.replace(i, '')

        params = ObjectDict({
            "salary_top": salary_top,
            "salary_bottom": salary_bottom,
            "salary_negotiable": salary_negotiable,
            "keywords": keywords,
            "city": city,
            "industry": industry,
            "did": did
        })

        self.logger.debug("get_es_positions_params: %s" % params)
        es_res = yield self.es_ds.get_es_positions(params, page_from, page_size)

        es_result = es_res.hits.hits
        total = es_res.get("hits", {}).get("total", 0)

        return es_result, total

    @gen.coroutine
    def opt_es_position(self, position_id):
        """ 搜索职位
        :param position_id:
        """

        es_res = yield self.es_ds.get_es_position(position_id)
        return es_res

    @gen.coroutine
    def opt_agg_positions(self, locale, es_res, user_id, city):
        """ 处理搜索职位结果
        :param es_res:
        :param user_id:
        :param city: 如果用户在搜索条件里面输入了选择的城市，
        那么不管该职位实际在哪些城市发布，在显示在列表页的时候，只显示用户选择的地址
        """

        city_list = split(city, [","]) if city else list()

        hot_positons = list()
        pos_pids = list()
        if es_res:
            for item in es_res:
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

                hot_positon = ObjectDict({
                    "id": item.get("_source").get("position").get("id"),
                    "title": item.get("_source").get("position").get("title"),
                    "salary": gen_salary(item.get("_source").get("position").get("salary_top"), item.get("_source").get("position").get("salary_bottom")),
                    "team": item.get("_source").get("team", {}).get("name",""),
                    "degree": gen_degree_v2(int(item.get("_source").get("position").get("degree")), item.get("_source").get("position").get("degree_above"), locale),
                    "experience":  gen_experience_v2(item.get("_source").get("position").get("experience"), item.get("_source").get("position").get("experience_above"), locale),
                    "has_team": True if item.get("_source").get("team", {}) else False,
                    "team_img": team_img,
                    "job_img": job_img,
                    "company_img": company_img,
                    "resources": self._gen_resources(item.get("_source").get("jd_pic",{}), item.get("_source").get("company",{}), item.get("_source").get("newjd_status",0)),
                    "user_status": 0,
                    "city": city,
                    "company": company,
                })
                pos_pids.append(item.get("_source").get("position").get("id"))
                hot_positons.append(hot_positon)

        # 处理 0: 未阅，1：已阅，2：已收藏，3：已投递
        positions = yield self._opt_user_positions_status(hot_positons, pos_pids, user_id)

        return positions

    @gen.coroutine
    def opt_jd_home_img(self, item):
        """ 处理JD首页行业默认图
        :param item:
        """

        industry_type = 0
        if item.get("_source", {}).get("company", {}).get("industry_type", None):
            industry_type = item.get("_source", {}).get("company", {}).get("industry_type")

        team_img = qx_const.JD_BACKGROUND_IMG.get(industry_type).get("team_img") if \
            qx_const.JD_BACKGROUND_IMG.get(industry_type) else qx_const.JD_BACKGROUND_IMG.get(0).get("team_img")
        job_img = qx_const.JD_BACKGROUND_IMG.get(industry_type).get("job_img") if \
            qx_const.JD_BACKGROUND_IMG.get(industry_type) else qx_const.JD_BACKGROUND_IMG.get(0).get("job_img")
        company_img = qx_const.JD_BACKGROUND_IMG.get(industry_type).get("company_img") if \
            qx_const.JD_BACKGROUND_IMG.get(industry_type) else qx_const.JD_BACKGROUND_IMG.get(0).get("company_img")

        if item.get("_source", {}).get("team",{}).get("resource", {}) \
            and item.get("_source", {}).get("team",{}).get("resource", {}).get("res_type", 0) == 0:
            team_img = item.get("_source").get("team",{}).get("resource",{}).get("res_url")

        if item.get("_source", {}).get("jd_pic",{}).get("position_pic",{}).get("first_pic",{}):
            job_img = item.get("_source").get("jd_pic",{}).get("position_pic",{}).get("first_pic",{}).get("res_url")

        if item.get("_source", {}).get("company", {}).get("banner", None):
            company_img = ujson.loads(item.get("_source", {}).get("company", {}).get("banner", None)).get("banner0")

        return make_static_url(team_img), make_static_url(job_img), make_static_url(company_img)

    @gen.coroutine
    def opt_agg_company(self, es_res):
        """ 处理热招企业，包括企业信息，搜索结果中的城市合集，在招企业职位数
        :param es_res:
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

    def _gen_resources(self, jd_pic, company, newjd_status):
        """ 处理图片逻辑
        :param jd_pic:
        :param company_type:
        :param newjd_status: 是否新 JD，2：新 JD 其他非新 JD
        """

        pic_list = list()
        if newjd_status == 2:
            # 新 JD
            if jd_pic.get("position_pic"):
                pic_list += jd_pic.get("position_pic").get("other_pic")
            if jd_pic.get("team_pic"):
                pic_list += jd_pic.get("team_pic").get("other_pic")
            if jd_pic.get("company_pic"):
                pic_list += jd_pic.get("company_pic").get("other_pic")
        else:
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
    def _opt_user_positions_status(self, hot_positions, pids, user_id):
        """
        处理 0: 未阅，1：已阅，2：已收藏，3：已投递
        :param pids:
        :param hot_positions:
        :param user_id:
        :return:
        """

        if not user_id or not pids:
            return hot_positions

        ret = yield self.thrift_searchcondition_ds.get_user_position_status(user_id, pids)
        if ret.positionStatus:
            for item in hot_positions:
                for key, value in ret.positionStatus.items():
                    if item.get("id") == key:
                        item["user_status"] = value

        return hot_positions
