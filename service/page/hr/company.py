# coding=utf-8

# Copyright 2016 MoSeeker

import re
from util.common import ObjectDict
from tornado import gen
from service.page.base import PageService


class CompanyPageService(PageService):
    def __init__(self, logger):
        super(CompanyPageService, self).__init__(logger)

    @gen.coroutine
    def get_company(self, conds, need_conf=None, fields=None):

        """
        获得公司信息
        :param conds:
        :param fields: 示例:
        conds = {
            "id": company_id
        }
        :return:
        """

        fields = fields or []
        need_conf = need_conf or False

        # 公司主表
        company = yield self.hr_company_ds.get_company(conds, fields)

        # 公司副表
        if need_conf:
            conds = {
                "company_id": company.get("id"),
            }
            company_conf_res = yield self.hr_company_conf_ds.get_company_conf(conds)

            # 搜索页页面栏目排序
            search_seq = []
            search_seq_tmp = re.split("#", company_conf_res.get("search_seq") or self.plat_constant.LANDING_SEQ)
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
                "conf_newjd_status": company_conf_res.get("newjd_status"),
                "conf_teamname_custom": company_conf_res.get("teamname_custom"),  # 职位部门字段名称
                "conf_application_time": company_conf_res.get("application_time"),  # 新JD开通申请时间
            })

            # 处理公司自定义团队名称
            conf_teamname_custom = company_conf.get("conf_teamname_custom")
            if conf_teamname_custom.strip():
                teamname_custom = ObjectDict({'teamname_custom': conf_teamname_custom.strip()})
            else:
                teamname_custom = ObjectDict({'teamname_custom': self.constant.TEAMNAME_CUSTOM_DEFAULT})
            company_conf.update(ObjectDict({"conf_teamname_custom": teamname_custom}))

            company.update(company_conf)

        raise gen.Return(company)

    @gen.coroutine
    def get_companys_list(self, conds, fields, options=None, appends=None):

        """
        获得公司列表
        :param conds:
        :param fields:
        :param options:
        :param appends:
        :return:
        """

        options = options or []
        appends = appends or []

        positions_list = yield self.hr_company_ds.get_companys_list(conds, fields, options, appends)
        raise gen.Return(positions_list)

    @gen.coroutine
    def get_real_company_id(self, publisher, company_id):
        """获得职位所属公司id
        公司有母公司和子公司之分，
        如果取母公司，则取 current_user.company，如果取职位对应的公司（可能是子公司，可能是母公司）则使用该方法
        1.首先根据 hr_company_account 获得 hr 帐号与公司之间的关系，获得company_id
        2.如果1取不到，则直接取职位中的 company_id"""

        hr_company_account = yield self.hr_company_account_ds.get_company_account(conds={"account_id": publisher})
        real_company_id = hr_company_account.company_id or company_id

        raise gen.Return(real_company_id)

    @gen.coroutine
    def save_survey(self, fields, options=None, appends=None):
        """保存公司 survey， 在公司 profile 主页保存"""
        options = options or []
        appends = appends or []

        lastrowid = yield self.campaign_company_survey_ds.create_survey(fields)
        raise gen.Return(lastrowid)

    @gen.coroutine
    def get_company_conf(self, company_id, fields):
        company_conf = yield self.hr_company_conf_ds.get_company_conf({"company_id": company_id}, fields)
        raise gen.Return(company_conf)

