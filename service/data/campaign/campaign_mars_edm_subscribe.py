# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class CampaignMarsEdmSubscribeDataService(DataService):

    @gen.coroutine
    def get_mars_user(self, conds, fields=None, appends=None):

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_mars_user][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds,
                                                                                                     type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.campaign_mars_edm_subscribe_dao.fields_map.keys())

        response = yield self.campaign_mars_edm_subscribe_dao.get_record_by_conds(
            conds=conds, fields=fields, appends=appends)
        raise gen.Return(response)

    @gen.coroutine
    def update_mars_user(self, conds, fields=None):

        if not conds or not fields:
            self.logger.warning("Warning:[update_mars_user][invalid parameters], Detail:[conds: {0}, "
                                "fields: {1}]".format(conds, fields))
            raise gen.Return(False)

        ret = yield self.campaign_mars_edm_subscribe_dao.update_by_conds(
            conds=conds,
            fields=fields)

        raise gen.Return(ret)
