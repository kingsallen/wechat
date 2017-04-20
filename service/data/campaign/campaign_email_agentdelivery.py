# coding=utf-8

from tornado import gen
from service.data.base import DataService


class CampaignEmailAgentdeliveryDataService(DataService):

    @gen.coroutine
    def create_campaign_email_agentdelivery(self, fields):
        lastrowid = yield self.campaign_email_agentdelivery_dao.insert_record(
            fields)
        raise gen.Return(lastrowid)
