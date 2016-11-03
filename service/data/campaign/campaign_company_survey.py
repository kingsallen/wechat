# coding=utf-8

from tornado import gen
from service.data.base import DataService


class CampaignCompanySurveyDataService(DataService):

    @gen.coroutine
    def create_survey(self, fields):
        lastrowid = yield self.campaign_company_survey_dao.insert_record(
            fields)
        raise gen.Return(lastrowid)
