# coding=utf-8

# Copyright 2016 MoSeeker

import re
from tornado.util import ObjectDict
from tornado import gen
from service.page.base import PageService

class CompanyPageService(PageService):

    @gen.coroutine
    def get_company(self, conds, need_conf=False, fields=[]):

        '''
        获得公司信息
        :param conds:
        :param fields: 示例:
        conds = {
            "id": company_id
        }
        :return:
        '''

        # 公司主表
        company = yield self.hr_company_ds.get_company(conds, fields)

        # 公司副表
        if need_conf:
            conds = {
               "company_id" : company.get("id"),
            }
            company_conf_res = yield self.hr_company_conf_ds.get_company_conf(conds)

            # 搜索页页面栏目排序
            search_seq = []
            search_seq_tmp = re.split(u"#", company_conf_res.get("search_seq") or self.plat_constant.LANDING_SEQ)
            for item in search_seq_tmp:
                # 若存在自定义字段值，则更新标题
                landing = self.plat_constant.LANDING.get(int(item))
                landing["index"] = item
                if company_conf_res.get("job_custom_title") and item == self.plat_constant.LANDING_INDEX_CUSTOM:
                    landing["name"] = company_conf_res.get("job_custom_title")
                search_seq.append(landing)

            # 避免副表字段与主表重复
            company_conf = ObjectDict({
                "conf_theme_id": company_conf_res.get("theme_id"),
                "conf_hb_throttle": company_conf_res.get("hb_throttle"),
                "conf_app_reply": company_conf_res.get("app_reply"),
                "conf_employee_binding": company_conf_res.get("employee_binding"),
                "conf_recommend_presentee": company_conf_res.get("recommend_presentee"),
                "conf_recommend_success": company_conf_res.get("recommend_success"),
                "conf_forward_message": company_conf_res.get("forward_message"),
                "conf_job_custom_title": company_conf_res.get("job_custom_title"),
                "conf_search_seq": search_seq,
                "conf_search_img": company_conf_res.get("search_img"),
            })
            company.update(company_conf)

        raise gen.Return(company)

    @gen.coroutine
    def get_companys_list(self, conds, fields, options=[], appends=[]):

        '''
        获得公司列表
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        '''

        positions_list = yield self.hr_company_ds.get_companys_list(conds, fields, options, appends)
        raise gen.Return(positions_list)