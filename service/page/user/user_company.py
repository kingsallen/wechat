# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from tornado.util import ObjectDict
from tornado import gen
from service.page.base import PageService
from tests.dev_data.user_company_data import data1, data2, data3, data4


class UserCompanyPageService(PageService):

    @gen.coroutine
    def get_company_follows(self, conds, fields=[]):
        fields = ['id', 'company_id', 'user_id']
        fans = yield self.wx_user_company_ds.get_user(conds, fields)
        raise gen.Return(fans)

    @gen.coroutine
    def get_companay_data(self, param):
        '''

        Develop Status: To be modify with real data.

        :param param: dict include target user company ids.
        :return: dict data to render template
        '''
        user_id, company_id = param.get('user_id'), param.get('company_id')
        response = ObjectDict({'status': 1, 'message': 'failure'})
        company = ObjectDict({
            'name': '仟寻招聘',
            'description': 'help people find job'
        })
        follow_company = yield self.wx_user_company_ds.get_fllw_cmpy(
                                user_id, company_id)
        visit_company = yield self.wx_user_company_ds.get_visit_cmpy(
                                user_id, company_id)

        data = ObjectDict({'company': company})
        data.templates_total = 4
        data.relation = ObjectDict({
            'follow': 1 if follow_company else 0,
            'want_visit': 1 if visit_company else 0
        })
        data.templates = [
            ObjectDict({'type': 1, 'titile': 'template 1', 'data': data1}),
            ObjectDict({'type': 2, 'titile': 'template 2', 'data': data2}),
            ObjectDict({'type': 3, 'titile': 'template 3', 'data': data3}),
            ObjectDict({'type': 4, 'titile': 'template 4', 'data': data4}),
        ]
        response.data = data

        raise gen.Return(response)

    @gen.coroutine
    def set_company_follow(self, param):
        response = yield self.wx_user_company_ds.set_cmpy_fllw(
                            user_id=param.get('user_id'),
                            company_id=param.get('company_id'),
                            status=param.get('status'),
                            source=param.get('source', 0))

        raise gen.Return(response)

    @gen.coroutine
    def set_visit_company(self, param):
        response = yield self.wx_user_company_ds.set_visit_cmpy(
                                user_id=param.get('user_id'),
                                company_id=param.get('company_id'),
                                status=param.get('status'),
                                source=param.get('source', 0))

        raise gen.Return(response)




