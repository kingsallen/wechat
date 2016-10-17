# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.17

"""

from tornado import gen
from service.data.base import *


class UserCompanyVisitReqDataService(DataService):

    @gen.coroutine
    def _get_foll_cmpy(self, conds, fields=[]):
        if not self._condition_isvalid(conds, 'get_foll_cmpy'):
            raise gen.Return(None)
        if not fields:
            fields = self.hr_wx_wechat_dao.fields_map.keys()
        try:
            response = yield self.user_company_follows_dao.get_list_by_conds(
                                    conds, fields)
        except Exception as error:
            self.logger(error)
            raise gen.Return(None)

        raise gen.Return(response)

    @gen.coroutine
    def get_visit_cmpy(self, user_id, company_id=None):
        conds = {'user_id': [user_id, '='], 'company_id': [company_id, '=']} \
            if company_id is not None else {'user_id': [user_id, '=']}
        company = yield self._get_visit_cmpy(conds, ['id', 'company_id'])

        raise gen.Return(company)

    @gen.coroutine
    def set_visit_cmpy(self, user_id, company_id, status, source):
        conds = {'user_id': [user_id, '='], 'company_id': [company_id, '=']}
        company = yield self._get_visit_cmpy(conds,
                                fields=['id', 'user_id', 'company_id'])
        if company:
            try:
                self.user_company_visit_req_dao.update_by_conds(conds,
                        fields={'status': str(status), 'source': str(source)})

            except Exception as error:
                self.logger(error)
                raise gen.Return(False)
        else:
            try:
                self.user_company_visit_req_dao.insert_record({
                    'user_id': user_id,
                    'company_id': company_id,
                    'status': status,
                    'source': source
                })
            except Exception as error:
                self.logger(error)
                raise gen.Return(False)

        raise gen.Return(True)
