# coding=utf-8

# @Time    : 4/25/17 14:43
# @Author  : panda (panyuxin@moseeker.com)
# @File    : campaign_recommend_company.py
# @DES     :

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache


class CampaignRecommendCompanyDataService(DataService):

    # @cache(ttl=300)
    @gen.coroutine
    def get_campaign_recommend_company(self, conds, fields=None, options=None, appends=None, index='', params=None):

        fields = fields or []
        options = options or []
        appends = appends or []
        params = params or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_campaign_recommend_company][invalid parameters], Detail:[conds: {0}, "
                        "type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.campaign_recommend_company_dao.fields_map.keys())

        response = yield self.campaign_recommend_company_dao.get_list_by_conds(conds, fields, options, appends, index, params)
        raise gen.Return(response)
