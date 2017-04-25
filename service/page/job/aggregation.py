# coding=utf-8

# @Time    : 4/18/17 11:57
# @Author  : panda (panyuxin@moseeker.com)
# @File    : aggregation.py
# @DES     : 聚合号列表页

import re
from tornado import gen
import conf.common as const
from service.page.base import PageService
from util.common import ObjectDict
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
    def get_hot_company(self, salary_top, salary_bottom, salary_negotiable, keywords, city, industry, page_no, page_size):

        params = ObjectDict({
            "salary_top": salary_top,
            "salary_bottom": salary_bottom,
            "salary_negotiable": salary_negotiable,
            "keywords": keywords,
            "city": city,
            "industry": industry
        })

        es_res = yield self.es_ds.get_es_position(params)

        result = self._opt_agg_company(es_res)

        # if es_res.aggregations:
        #     company_ids = es_res.aggregations.all_count.value
        #     self.logger.debug("company_ids:{}".format(company_ids))
        #     recommend_companys = yield self.campaign_recommend_company_ds.get_campaign_recommend_company(conds={
        #         "disable": 0
        #     }, fields=["company_id"], appends=["ORDER BY weight ASC"])
        #     sorted_ids = company_ids
        #     if recommend_companys:
        #         recommend_companys_ids = [item.company_id for item in recommend_companys]
        #         # 分别获得 es的 company_id，和运营排序 company_id，再根据运营 company_id 排序整个 es 的 company_id
        #         for id in recommend_companys_ids:
        #             if id in company_ids:
        #                 company_ids.insert(0, id)
        #
        #         sorted_ids = list(set(company_ids))
        #         sorted_ids.sort(key=company_ids.index)
        #
        # sorted_ids = sorted_ids[:9]
        # self.logger.debug("sorted_ids:{}".format(sorted_ids))
        # result = list()
        # for id in sorted_ids:
        #     agg_company = ObjectDict()
        #     company_info = yield self.hr_company_ds.get_company(conds={"id":id})
        #     position_cnt = yield self._get_company_positions_cnt(id)
        #     agg_company["id"] = company_info.id
        #     agg_company["logo"] = make_static_url(company_info.logo or const.COMPANY_HEADIMG)
        #     agg_company["abbreviation"] = company_info.abbreviation
        #     agg_company["position_count"] = position_cnt.count_id if position_cnt else 0
        #     result.append(agg_company)

        return result

    def _opt_agg_company(self, es_res):


        if es_res.hits:
            result = ObjectDict()
            for item in es_res.hits.hits:
                print("---"*10)
                print(item)
                city_list = re.split(",", item.get("_source").get("position").get("city")) \
                    if item.get("_source").get("position").get("city") else list()
                company_id_str = str(item.get("_source").get("company").get("id"))
                if result.get(company_id_str):
                    print("19191919191919191919")
                    print(city_list)
                    print(result[company_id_str].get("city"))
                    if city_list:
                        city_rep = result[company_id_str].get("city") + city_list
                        print("3737373373737373737373737")
                        print(city_rep)
                        result[company_id_str].city = list(set(city_rep))

                    result[company_id_str].position_cnt += 1

                else:
                    result[company_id_str] = ObjectDict({
                        "company": item.get("_source").get("company"),
                        "city": city_list,
                        "position_cnt":  1,
                    })
                print("+++"*10)
                print(result)
                print("---" * 10)

        print (result)








