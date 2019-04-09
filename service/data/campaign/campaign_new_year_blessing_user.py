# coding=utf-8

# Copyright 2018 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common import ObjectDict


class CampaignNewYearBlessingUserDataService(DataService):

    @gen.coroutine
    def get_blessing_user(self, conds, fields=None, appends=None):

        if not self._valid_conds(conds):
            self.logger.warning(
                "Warning:[get_blessing_user][invalid parameters], Detail:[conds: {0}, type: {1}]".format(conds,
                                                                                                     type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.campaign_new_year_blessing_user_dao.fields_map.keys())

        response = yield self.campaign_new_year_blessing_user_dao.get_record_by_conds(
            conds=conds, fields=fields, appends=appends)
        raise gen.Return(response)
