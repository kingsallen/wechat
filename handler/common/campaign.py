# coding=utf-8

from tornado import gen

from handler.metabase import MetaBaseHandler
from util.common.decorator import handle_response


class AlipayCampaignCompanyHandler(MetaBaseHandler):
    # @cache(ttl=60 * 60)
    @gen.coroutine
    def _get(self, campaign_id):
        """
        支付宝活动Landing页, 公司
        :param campaign_id: 活动id
        :return: render页面
        """
        campaign = yield self.campaign_ps.get_alipay_campaign_by_id(campaign_id)
        if not campaign:
            return None
        else:
            return self.render_string(template_name="h5/alipay/index.html", campaign=campaign)

    @handle_response
    @gen.coroutine
    def get(self, campaign_id):
        page_content = yield self._get(campaign_id)
        if not page_content:
            self.write_error(404)
        else:
            self.finish(page_content)


class AlipayCampaignPositionHandler(MetaBaseHandler):
    # @cache(ttl=60*60)
    @gen.coroutine
    def _get(self, campaign_id, company_id):
        """
        支付宝活动的多个公司的职位列表页面
        :param campaign_id: 活动id
        :return: render页面
        """
        campaign = yield self.campaign_ps.get_alipay_campaign_by_id(campaign_id)
        if not campaign:
            return None
        else:
            selected_company = campaign.get_company(company_id)
            return self.render_string(template_name="h5/alipay/list.html", campaign=campaign, company=selected_company)

    @handle_response
    @gen.coroutine
    def get(self, campaign_id, company_id):
        company_id = int(company_id)
        page_content = yield self._get(campaign_id, company_id)
        if not page_content:
            self.write_error(404)
        else:
            self.finish(page_content)
