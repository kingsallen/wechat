# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from util.common import ObjectDict
from tornado import gen
from service.page.base import PageService
from tests.dev_data.user_company_data import data1, data2, data3,\
                                             data4_1, data4_2, data50


class UserCompanyPageService(PageService):

    @gen.coroutine
    def get_company_follows(self, conds, fields=[]):
        fields = ['id', 'company_id', 'user_id']
        fans = yield self.user_company_follows_ds.get_user(conds, fields)
        raise gen.Return(fans)

    @gen.coroutine
    def get_companay_data(self, param, team_flag):
        """
        Develop Status: To be modify with real data.

        :param param: dict include target user company ids.
        :return: dict data to render template
        """
        user_id, company_id = param.get('user_id'), param.get('company_id')
        response = ObjectDict({'status': 0, 'message': 'sucdess'})
        header = ObjectDict({
            'type': 'team' if team_flag else 'company',
            'name': '仟寻招聘',
            'description': 'help people find job',
            'icon': '',
            'banner': '',
        })
        follow_company = yield self.user_company_follows_ds.get_fllw_cmpy(
                                user_id, company_id)
        visit_company = yield self.user_company_visit_req_ds.get_visit_cmpy(
                                user_id, company_id)

        data = ObjectDict({'header': header})
        data.templates_total = 4
        data.relation = ObjectDict({
            'follow': self.constant.YES if follow_company \
                        else self.constant.NO,
            'want_visit': self.constant.YES if visit_company \
                        else self.constant.NO
        })
        data.templates = [
            ObjectDict({'type': 1, 'sub_type': 'full', 'title': 'template 1',
                        'data': data1, 'more_link': 'more_link_test'}),
            ObjectDict({'type': 1, 'sub_type': 'middle', 'title': 'template 1',
                        'data': data1}),
            ObjectDict({'type': 1, 'sub_type': 'less', 'title': 'template 1',
                        'data': data1}),
            ObjectDict({'type': 2, 'title': 'template 2', 'data': data2}),
            ObjectDict({'type': 3, 'title': 'template 3', 'data': data3}),
            ObjectDict({'type': 4, 'sub_type': 0, 'title': 'template 4',
                        'data': data4_1}),
            ObjectDict({'type': 4, 'sub_type': 1, 'title': 'template 4',
                        'data': data4_2}),
            ObjectDict({'type': 5, 'title': 'template 5', 'data': None}),
            ObjectDict({'type': 50, 'title': 'template 50', 'data': data50}),
        ]
        response.data = data

        raise gen.Return(response)

    @gen.coroutine
    def set_company_follow(self, param):
        response = yield self.user_company_follows_ds.set_cmpy_fllw(
                            user_id=param.get('user_id'),
                            company_id=param.get('company_id'),
                            status=param.get('status'),
                            source=param.get('source', 0))

        raise gen.Return(response)

    @gen.coroutine
    def set_visit_company(self, param):
        response = yield self.user_company_visit_req_ds.set_visit_cmpy(
                                user_id=param.get('user_id'),
                                company_id=param.get('company_id'),
                                status=param.get('status'),
                                source=param.get('source', 0))

        raise gen.Return(response)




