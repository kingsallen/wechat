# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.10.11

"""

from tornado import gen

from service.page.base import PageService
from tests.dev_data.user_company_data import WORKING_ENV, TEAMS, MEMBERS, \
    data2, TEAM_EB, TEAM_BD, TEAM_CS, TEAM_RD, data4_1, data50
from util.common import ObjectDict
from util.tool.url_tool import make_url


class UserCompanyPageService(PageService):

    @gen.coroutine
    def get_company_follows(self, conds, fields=[]):
        fields = ['id', 'company_id', 'user_id']
        fans = yield self.user_company_follow_ds.get_user(conds, fields)
        raise gen.Return(fans)

    @gen.coroutine
    def get_companay_data(self, handler_params, param, team_flag):
        """Develop Status: To be modify with real data.
        :param handler_params:
        :param param:
        :param team_flag:
        :return:
        """
        user_id, company_id = param.get('user_id'), param.get('company_id')
        response = ObjectDict({'status': 0, 'message': 'sucdess'})

        if not team_flag:
            header = ObjectDict({
                'type':        'company',
                'name':        '仟寻 MoSeeker',
                'description': "你的职场向导",
                'icon':        '',
                'banner':
                    'https://cdn.moseeker.com/upload/company_profile/qx'
                    '/banner_qx.jpeg',
            })
        else:
            header = ObjectDict({
                'type':        'team',
                'name':        '我们的团队',
                'description': "",
                'icon':        '',
                'banner':
                    'https://cdn.moseeker.com/upload/company_profile/qx'
                    '/banner_qx.jpeg',
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
            self._add_team_data(handler_params, data)
        else:
            self._add_company_data(handler_params, data)

        response.data = data

        raise gen.Return(response)

    @staticmethod
    def _add_company_data(hander_params, data):
        """构建公司主页的豆腐干们"""

        data.templates = [
            ObjectDict({
                'type': 1,
                'sub_type': 'less',
                'title': '办公环境',
                'data': WORKING_ENV,
                'more_link': ''
            }),
            ObjectDict({'type': 2, 'title': 'template 2', 'data': data2}),
            ObjectDict({
                'type':      1,
                'sub_type':  'less',
                'title':     '我们的团队',
                'data':      TEAMS,
                'more_link': ''
            }),
            ObjectDict({
                'type':      1,
                'sub_type':  'less',
                'title':     '在这里工作的人们',
                'data':      MEMBERS,
                'more_link': ''
            }),
            ObjectDict({
                'type': 4,
                'sub_type': 0,
                'title': '公司大事件',
                'data': data4_1
            }),
            # 可能感兴趣的公司，暂时不做
            # ObjectDict({'type': 4, 'sub_type': 1, 'title': '你可能感兴趣的公司',
            #             'data': data4_2}),
            ObjectDict({'type': 5, 'title': 'template 5', 'data': None}),
            ObjectDict({'type': 50, 'title': 'address', 'data': data50}),
        ]
        data.template_total = len(data.templates)

    @staticmethod
    def _add_team_data(hander_params, data):
        """构建团队主页的豆腐干们"""

        data.templates = [
            ObjectDict({
                'type':      1,
                'sub_type':  'full',
                'title':     '研发团队',
                'data':      TEAM_RD,
                'more_link': make_url('/m/teams/rd', hander_params)
            }),

            ObjectDict({
                'type':      1,
                'sub_type':  'full',
                'title':     '客户成功团队',
                'data':      TEAM_CS,
                'more_link': make_url('/m/teams/cs', hander_params)
            }),

            ObjectDict({
                'type':      1,
                'sub_type':  'full',
                'title':     '商务拓展团队',
                'data':      TEAM_BD,
                'more_link': make_url('/m/teams/bd', hander_params)
            }),

            ObjectDict({
                'type':      1,
                'sub_type':  'full',
                'title':     '雇主品牌团队',
                'data':      TEAM_EB,
                'more_link': make_url('/m/teams/eb', hander_params)
            }),
        ]
        data.template_total = len(data.templates)

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
