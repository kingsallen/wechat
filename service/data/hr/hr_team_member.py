# coding=utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from service.data.base import DataService
from util.common.decorator import cache
from util.common import ObjectDict


class HrTeamMemberDataService(DataService):

    # @cache(ttl=60)
    @gen.coroutine
    def get_team_member(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_team_member][invalid parameters], \
                    Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(ObjectDict())

        if not fields:
            fields = list(self.hr_team_member_dao.fields_map.keys())

        response = yield self.hr_team_member_dao.get_record_by_conds(conds, fields)
        raise gen.Return(response)

    # @cache(ttl=60)
    @gen.coroutine
    def get_team_member_list(self, conds, fields=None):

        fields = fields or []

        if conds is None or not (isinstance(conds, (dict, str))):
            self.logger.warning("Warning:[get_team_member_list][invalid parameters], \
                    Detail:[conds: {0}, type: {1}]".format(conds, type(conds)))
            raise gen.Return(list())

        if not fields:
            fields = list(self.hr_team_member_dao.fields_map.keys())

        response = yield self.hr_team_member_dao.get_list_by_conds(conds, fields)
        raise gen.Return(response)
