# coding=utf-8

import re
import urllib

from tornado import gen

from conf import common
from service.page.base import PageService
from setting import settings
from util.common import ObjectDict
from util.tool import str_tool


class AlipayCampaign:
    def __init__(self, id):
        self.id = id
        self.companies = []

    def add_company(self, alipay_campaign_company):
        self.companies.append(alipay_campaign_company)

    def get_company(self, company_id):
        selected_companies = [company for company in self.companies if company.id == company_id]
        if selected_companies:
            return selected_companies[0]
        else:
            return None


class AlipayCampaignCompany:
    DEFAULT_COMPANY_LOGO = common.COMPANY_HEADIMG

    def __init__(self, infra_company, company_name, company_industry):
        # use
        self.id = infra_company.id
        self.abbreviation = company_name
        self.industry = company_industry
        self.logo_path = infra_company.logo
        self.positions = []

    def add_position(self, position):
        """

        :param position: AlipayCampaignPosition
        :return:
        """
        if self.filter_position(position):
            self.modify_position_title(position)
            self.positions.append(position)
        else:
            pass

    def modify_position_title(self, position):
        pass

    @property
    def positions_num(self):
        return len(self.positions)

    @property
    def logo(self):
        logo = next(l for l in (self.logo_path, self.DEFAULT_COMPANY_LOGO) if l)
        return urllib.parse.urljoin(settings["static_domain"], logo)

    @property
    def cities(self):
        all_cities = set(position.city for position in self.positions if bool(position.city))
        return " | ".join(list(all_cities)[:3]) + ("等" if len(all_cities) > 3 else "")

    def filter_position(self, position):
        return True


class AlipayCampaignCompanyWalmart(AlipayCampaignCompany):
    def filter_position(self, position):
        return bool(re.match(r".*管理培训生.*", position.title))


class AlipayCampaignCompanyPhillips(AlipayCampaignCompany):
    def filter_position(self, position):
        return bool(re.match(r".*[(（]校园招聘[)）].*", position.title))


class AlipayCampaignCompanyTE(AlipayCampaignCompany):
    def filter_position(self, position):
        return bool(re.match(r".*【Campus Hire】.*", position.title))

    def modify_position_title(self, position):
        position.title = position.title.replace("【Campus Hire】", "")


class AlipayCampaignCompanyLiepin(AlipayCampaignCompany):
    def filter_position(self, position):
        return True


class AlipayCampaignPosition:
    alipay_url_formatter = "http://www.anijue.com/p/q/campusjob/index.html#/jobInfo/?jobType=3&jobId={}"

    def __init__(self, infra_position):
        self.id = infra_position.id
        self.title = infra_position.title
        self.city = infra_position.city
        self.alipay_job_id = infra_position.alipayJobId
        self.salary_top = infra_position.salaryTop
        self.salary_bottom = infra_position.salaryBottom

    @property
    def salary(self):
        return str_tool.gen_salary(self.salary_top, self.salary_bottom)

    @property
    def url(self):
        return self.alipay_url_formatter.format(self.alipay_job_id)


class CampaignNotFoundError(Exception): pass


class CampaignPageService(PageService):
    # 写死的几个公司
    campaigns = {
        "1": [ObjectDict({"id": 76, "name": "沃尔玛", "industry": "快速消费品", "klass": AlipayCampaignCompanyWalmart}),
              ObjectDict({"id": 1291, "name": "飞利浦", "industry": "多元化集团", "klass": AlipayCampaignCompanyPhillips}),
              ObjectDict({"id": 89816, "name": "泰科电子", "industry": "电子技术", "klass": AlipayCampaignCompanyTE}),
              ObjectDict({"id": 203536, "name": "猎聘网", "industry": "互联网", "klass": AlipayCampaignCompanyLiepin})]
    }

    @gen.coroutine
    def get_alipay_campaign_by_id(self, campaign_id):
        """
        根据campaign_id获取整个活动内容
        :param campaign_id: campaign活动id, int
        :return: AlipayCampaign
        """
        try:
            companies = yield self.get_alipay_campaign_companies(campaign_id)
            alipay_campaign = AlipayCampaign(campaign_id)
            campaign_companies = yield [
                self._get_alipay_campaign_company(campaign_id, company.id, company.name, company.industry, company.klass)
                for company in companies]
            for company in campaign_companies:
                alipay_campaign.add_company(company)
        except CampaignNotFoundError:
            return None
        else:
            return alipay_campaign

    @gen.coroutine
    def get_alipay_campaign_companies(self, campaign_id):
        """
        获取参与活动的公司, 目前写死的几家公司
        :param campaign_id:
        :return:
        """
        try:
            companies = self.campaigns[campaign_id]
        except KeyError:
            raise CampaignNotFoundError("Campaign(id: {}) not found".format(campaign_id))
        else:
            return companies

    @gen.coroutine
    def _get_alipay_campaign_company(self, campaign_id, company_id, company_name, company_industry, company_klass):
        """
        获取参与参与campaign的公司
        :param campaign_id:
        :param company_id: 公司id
        :param company_name: 公司名
        :return: AlipayCampaignCompany
        """
        # 公司
        result, infra_company = yield self.infra_company_ds.get_company_by_id({"id": company_id})
        assert (len(infra_company) == 1)
        alipay_campaign_company = company_klass(ObjectDict(infra_company[0]), company_name, company_industry)

        # 公司下参与活动的职位
        alipay_campaign_positions = yield self._get_alipay_campaign_company_positions(campaign_id, company_id)
        for alipay_campaign_position in alipay_campaign_positions:
            alipay_campaign_company.add_position(alipay_campaign_position)

        return alipay_campaign_company

    @gen.coroutine
    def _get_alipay_campaign_company_positions(self, campaign_id, company_id):
        """
        获取某公司参与campaign的职位列表
        :param campaign_id:
        :param company_id:
        :return: [AlipayCampaignPosition, ...]
        """
        infra_positions_info = yield self.infra_position_ds.get_third_party_synced_positions(company_id)
        infra_positions = infra_positions_info.get("positions", [])
        # infra_positions_num = infra_positions_info.get("positionNum", 0)
        alipay_positions = [AlipayCampaignPosition(ObjectDict(infra_position)) for infra_position in infra_positions]
        return alipay_positions

    @gen.coroutine
    def get_new_year_blessing_user(self, user_id):
        """
        获取用户的年度总结的数据
        :param user_id:
        :return:
        """
        user = yield self.campaign_new_year_blessing_user_ds.get_blessing_user({
            "sysuser_id": user_id
        })
        return user
