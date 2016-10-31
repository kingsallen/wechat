# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from util.common import ObjectDict
from tornado import gen
from service.page.base import PageService
from tests.dev_data.user_company_data import WORKING_ENV, TEAMS, MEMBERS, data2, data3,\
                                             data4_1, data4_2, data50


class UserCompanyPageService(PageService):

    @gen.coroutine
    def get_company_follows(self, conds, fields=[]):
        fields = ['id', 'company_id', 'user_id']
        fans = yield self.user_company_follow_ds.get_user(conds, fields)
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
            'name': '仟寻 MoSeeker',
            'description': "你的职场向导",
            'icon': '',
            'banner': 'https://cdn.moseeker.com/upload/company_profile/qx/banner_qx.jpeg',
        })
        conds = {'user_id': user_id, 'company_id': company_id}

        fllw_cmpy = yield self.user_company_follow_ds.get_fllw_cmpy(
                        conds=conds, fields=['id', 'company_id'])
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
                        conds=conds, fields=['id', 'company_id'])
        data = ObjectDict({'header': header})

        data.relation = ObjectDict({
            'follow':     self.constant.YES if fllw_cmpy else self.constant.NO,
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO
        })

        if team_flag:
            self._add_team_data(data)
        else:
            self._add_company_data(data)

        response.data = data

        raise gen.Return(response)

    @staticmethod
    def _add_company_data(data):
        """构建公司主页的豆腐干们"""
        data.template_total = 4

        data.templates = [

            ObjectDict({
                'type': 1,
                'sub_type': 'less',
                'title': '办公环境',
                'data': WORKING_ENV,
                'more_link': 'more_link_test'
            }),

            ObjectDict({'type': 2, 'title': 'template 2', 'data': data2}),

            ObjectDict({
                'type':      1,
                'sub_type':  'less',
                'title':     '我们的团队',
                'data':      TEAMS,
                'more_link': 'more_link_test'
            }),

            ObjectDict({
                'type':      1,
                'sub_type':  'less',
                'title':     '在这里工作的人们',
                'data':      MEMBERS,
                'more_link': 'more_link_test'
            }),


            ObjectDict({'type': 4, 'sub_type': 0, 'title': '公司大事件',
                        'data': data4_1}),

            ObjectDict({'type': 4, 'sub_type': 1, 'title': 'template 4',
                        'data': data4_2}),

            ObjectDict({'type': 5, 'title': 'template 5', 'data': None}),

            ObjectDict({'type': 50, 'title': 'template 50', 'data': data50}),

        ]

    @staticmethod
    def _add_team_data(data):
        """构建团队主页的豆腐干们"""
        data.template_total = 4
        data.templates = [
            # ObjectDict({
            #     'type': 1,
            #     'sub_type': 'full',
            #     'title': 'template 1',
            #     'data': data1,
            #     'more_link': 'more_link_test'}),
            #
            # ObjectDict({'type': 1, 'sub_type': 'middle', 'title': 'template 1',
            #             'data': data1}),
            #
            # ObjectDict({'type': 1, 'sub_type': 'less', 'title': 'template 1',
            #             'data': data1}),

            ObjectDict({'type': 2, 'title': 'template 2', 'data': data2}),

            ObjectDict({'type': 3, 'title': 'template 3', 'data': data3}),

            ObjectDict({'type': 4, 'sub_type': 0, 'title': 'template 4',
                        'data': data4_1}),

            ObjectDict({'type': 4, 'sub_type': 1, 'title': 'template 4',
                        'data': data4_2}),

            ObjectDict({'type': 5, 'title': 'template 5', 'data': None}),

            ObjectDict({'type': 50, 'title': 'template 50', 'data': data50}),

        ]

    @gen.coroutine
    def set_company_follow(self, param):
        """
        Store follow company.
        :param param: dict include target user company ids.
        :return:
        """
        user_id, company_id = param.get('user_id'), param.get('company_id'),
        status, source = param.get('status'), param.get('source', 0)

        conds = {'user_id': [user_id, '='], 'company_id': [company_id, '=']}
        company = yield self.user_company_follow_ds.get_fllw_cmpy(
            conds=conds, fields=['id', 'user_id', 'company_id'])

        if company:
            response = yield self.user_company_follow_ds.update_fllw_cmpy(
                conds=conds,
                fields={'status': status, 'source': source})
        else:
            response = yield self.user_company_follow_ds.create_fllw_cmpy(
                fields={'user_id': user_id, 'company_id': company_id,
                        'status': status, 'source': source})
        result = True if response else False

        raise gen.Return(result)

    @gen.coroutine
    def set_visit_company(self, param):
        """
        Store visiting company.
        :param param: dict include target user company ids.
        :return:
        """
        user_id, company_id = param.get('user_id'), param.get('company_id'),
        status, source = param.get('status'), param.get('source', 0)

        if int(status) == 0:
            # response.status, response.message = 1, 'ignore'
            raise gen.Return(False)

        conds = {'user_id': [user_id, '='], 'company_id': [company_id, '=']}
        company = yield self.user_company_visit_req_ds.get_visit_cmpy(
                            conds, fields=['id', 'user_id', 'company_id'])

        if company:
            response = yield self.user_company_visit_req_ds.update_visit_cmpy(
                            conds=conds,
                            fields={'status': status, 'source': source})
        else:
            response = yield self.user_company_visit_req_ds.create_visit_cmpy(
                fields={'user_id': user_id, 'company_id': company_id,
                        'status': status, 'source': source})

        result = True if response else False

        raise gen.Return(result)
