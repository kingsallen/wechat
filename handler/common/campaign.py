# coding=utf-8

from collections import namedtuple

from tornado import gen

import conf.common as const
import conf.path as path
from globals import redis
from handler.metabase import MetaBaseHandler
from util.common import ObjectDict
from util.common.decorator import handle_response
from util.tool.url_tool import make_url

CacheConfig = namedtuple("CacheConfig", ["use", "ttl", "cache_key"])


class CacheRenderMixin:
    def cache_render(self, template_name, cache_config, **kwargs):
        self.config_cache(cache_config)
        if self.cache_config.use:
            cached_html = self.get_page()
            if cached_html:
                self.logger.debug("got page from cache, key: {}".format(self.cache_config.cache_key))
                html = cached_html
            else:
                html = self.render_string(template_name, **kwargs)
                self.save_page(html)
            self.finish(html)
        else:
            self.render(template_name, **kwargs)

    def save_page(self, html):
        self.logger.debug("save page to cache, key: {}".format(self.cache_config.cache_key))
        try:
            redis.set(key=self.cache_config.cache_key, value=html, ttl=self.cache_config.ttl)
        except Exception as e:
            self.logger.error(e)

    def get_page(self):
        try:
            cached_html = redis.get(self.cache_config.cache_key)
        except Exception as e:
            self.logger.error(e)
            return None
        else:
            return cached_html

    def get_cache_render(self):
        return self

    def config_cache(self, conf: CacheConfig):
        """
        设置缓存配置, 不直接放在self下, 用一个属性来存防止命名冲突
        :param conf:
        :return: None
        """
        self.cache_config = conf


class AlipayCampaignCompanyHandler(MetaBaseHandler, CacheRenderMixin):
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
            cache_config = CacheConfig(use=False,
                                       ttl=60 * 60,
                                       cache_key="alipay_campaign_company:{}".format(campaign_id))
            self.cache_render(template_name="h5/alipay/index.html", cache_config=cache_config, campaign=campaign)


class AlipayCampaignPositionHandler(MetaBaseHandler, CacheRenderMixin):
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
            cache_config = CacheConfig(use=False,
                                       ttl=60 * 60,
                                       cache_key="alipay_campaign_position:{}".format(campaign_id))
            self.cache_render(template_name="h5/alipay/list.html", cache_config=cache_config, campaign=campaign)
