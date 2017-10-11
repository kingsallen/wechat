# coding=utf-8

from tornado import gen

import conf.common as const
import conf.path as path
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.url_tool import make_url


class AlipayCampaignCompanyHandler(MetaBaseHandler):
    def make_url(self, path, params=None, host="", protocol="https", escape=None, **kwargs):
        if not host:
            host = self.host
        return make_url(path, params, host, protocol, escape, **kwargs)

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        add_namespace = ObjectDict(
            env=self.env,
            make_url=self.make_url,
            const=const,
            path=path
        )
        namespace.update(add_namespace)
        return namespace

    @handle_response
    @gen.coroutine
    def get(self, campaign_id):
        """
        支付宝活动Landing页, 公司
        :param campaign_id: 活动id
        :return: render页面
        """
        campaign = yield self.campaign_ps.get_alipay_campaign_by_id(campaign_id)
        if not campaign:
            self.write_error(http_code=404)
        else:
            self.render(template_name="h5/alipay/index.html", campaign=campaign)


class AlipayCampaignPositionHandler(MetaBaseHandler):
    def make_url(self, path, params=None, host="", protocol="https", escape=None, **kwargs):
        if not host:
            host = self.host
        return make_url(path, params, host, protocol, escape, **kwargs)

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        add_namespace = ObjectDict(
            env=self.env,
            make_url=self.make_url,
            const=const,
            path=path
        )
        namespace.update(add_namespace)
        return namespace

    @handle_response
    @gen.coroutine
    def get(self, campaign_id):
        """
        支付宝活动的多个公司的职位列表页面
        :param campaign_id: 活动id
        :return: render页面
        """
        campaign = yield self.campaign_ps.get_alipay_campaign_by_id(campaign_id)
        if not campaign:
            self.write_error(http_code=404)
        else:
            self.render(template_name="h5/alipay/list.html", campaign=campaign)
