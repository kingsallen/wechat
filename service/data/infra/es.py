# coding=utf-8

import tornado.gen as gen

from service.data.base import DataService

from util.common.es import BaseES
from util.tool.es_tool import init_gamma_basic, rule_gamma_filters, init_gamma_position


class EsDataService(DataService):

    """对接ES服务
        referer: https://wiki.moseeker.com/application-api.md"""

    es = BaseES()

    @gen.coroutine
    def get_es_positions(self, params, page_from, page_size):
        """根据条件获得搜索结果列表
        """

        params = rule_gamma_filters(params)

        body = init_gamma_basic(params.keywords,
                                params.city,
                                params.industry,
                                params.salary_bottom,
                                params.salary_top,
                                params.salary_negotiable,
                                params.did,
                                page_from,
                                page_size)

        res = self.es.search(index="positions", body=body)
        raise gen.Return(res)

    @gen.coroutine
    def get_es_position(self, position_id):
        """根据条件获得具体搜索结果
        """

        body = init_gamma_position(position_id)

        self.logger.debug("init_gamma_position:{}".format(body))

        res = self.es.search(index="positions", body=body)
        raise gen.Return(res)
