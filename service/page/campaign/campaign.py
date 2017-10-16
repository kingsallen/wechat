# coding=utf-8

import re
import urllib

from tornado import gen

from service.page.base import PageService
from setting import settings
from util.common import ObjectDict


class AlipayCampaign:
    def __init__(self, id):
        self.id = id
        self.companies = []

    def add_company(self, alipay_campaign_company):
        self.companies.append(alipay_campaign_company)  # TODO: 去重


class AlipayCampaignCompany:
    DEFAULT_COMPANY_LOGO = "common/images/default-company-logo.jpg"

    def __init__(self, infra_company, company_name):
        # use
        self.id = infra_company.id
        self.abbreviation = company_name
        self.industry = infra_company.industry
        self.logo_path = infra_company.logo
        self.positions = []

    def add_position(self, position):
        """

        :param position: AlipayCampaignPosition
        :return:
        """
        if self.filter_position(position):
            self.positions.append(position)
        else:
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
        return " | ".join(list(all_cities)[:3])

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


class AlipayCampaignCompanyLiepin(AlipayCampaignCompany):
    def filter_position(self, position):
        return True


class AlipayCampaignPosition:
    alipay_url_formatter = "http://www.anijue.com/p/q/campusjob/index.html#/jobInfo/?jobType=3&jobId={}"

    def __init__(self, infra_position):
        self.id = infra_position.id
        self.title = infra_position.title
        self.city = infra_position.city
        self.lJobid = infra_position.lJobid
        self.salary_top = infra_position.salaryTop
        self.salary_bottom = infra_position.salaryBottom

    @property
    def salary(self):
        return " - ".join([str(self.salary_bottom) + "k", str(self.salary_top) + "k"])

    @property
    def url(self):
        return self.alipay_url_formatter.format(self.lJobid)


class CampaignNotFoundError(Exception): pass


class CampaignPageService(PageService):
    # 写死的几个公司
    campaigns = {
        "1": [ObjectDict({"id": 76, "name": "沃尔玛", "klass": AlipayCampaignCompanyWalmart}),
              ObjectDict({"id": 1291, "name": "飞利浦", "klass": AlipayCampaignCompanyPhillips}),
              ObjectDict({"id": 89816, "name": "泰科电子", "klass": AlipayCampaignCompanyTE}),
              ObjectDict({"id": 203536, "name": "猎聘网", "klass": AlipayCampaignCompanyLiepin})]
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
                self._get_alipay_campaign_company(campaign_id, company.id, company.name, company.klass)
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
    def _get_alipay_campaign_company(self, campaign_id, company_id, company_name, company_klass):
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
        alipay_campaign_company = company_klass(ObjectDict(infra_company[0]), company_name)

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


if __name__ == "__main__":
    from tornado.ioloop import IOLoop

    alipay_campaign_ps = AlipayCampaignPageService()


    @gen.coroutine
    def run():
        yield alipay_campaign_ps.get_alipay_campaign_by_id("aslfdkj")


    IOLoop.run_sync(run)
