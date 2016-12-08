# -*- coding=utf-8 -*-
# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.18

"""
from util.common import ObjectDict
from tornado import gen
from service.page.base import PageService
from util.tool import temp_date_tool
from util.tool.url_tool import make_url
from conf import path
from tests.dev_data.user_company_config import COMPANY_CONFIG

class TeamPageService(PageService):

    @gen.coroutine
    def get_sub_company(self, sub_company_id):
        sub_company = yield self.hr_company_ds.get_company(
            conds={'id': sub_company_id})

        raise gen.Return(sub_company)

    @gen.coroutine
    def get_team_by_id(self, team_id):
        team = yield self.hr_team_ds.get_team(conds={'id': team_id})

        raise gen.Return(team)

    @gen.coroutine
    def get_team_index(self, company, handler_param, sub_flag=False):
        """

        :param company: 当前需要获取数据的公司
        :param handler_param: 请求中参数
        :param sub_flag: 区分母公司和子公司标识， 用以明确团队资源获取方式
        :return:
        """
        data = ObjectDict(templates=[])

        # 根据母公司，子公司区分对待，获取团队信息
        if sub_flag:
            teams = yield self._get_sub_company_teams(self, company.id)
        else:
            teams = yield self.hr_team_ds.get_team_list(
                conds={'company_id': company.id})

        # 获取团队成员以及所需要的media信息
        team_media_dict = yield self.hr_media_ds.get_media_by_ids(
            [t.media_id for t in teams])
        all_members_dict = yield self._get_all_team_members(
            [t.id for t in teams])
        all_member_headimg_dict = yield self.hr_media_ds.get_media_by_ids(
            all_members_dict.get('all_headimg_list'))

        # 拼装模板数据
        data.header = temp_date_tool.make_header(company, team_flag=True)
        # 解析生成团队列表页中每个团队信息子模块
        data.templates = [
            temp_date_tool.make_team_index_template(
                team=t,
                team_medium=team_media_dict.get(t.media_id),
                more_link=make_url(path.TEAM_PATH.format(t.id), handler_param),
                member_list=[
                    temp_date_tool.make_team_member(
                        member=m,
                        headimg=all_member_headimg_dict.get(m.headimg_id)
                    ) for m in all_members_dict.get(t.id)]
            ) for t in teams
        ]
        data.template_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def get_team_detail(self, user, company, team, handler_param):
        """

        :param user: handler中的current_user
        :param company: 当前需要获取数据的公司
        :param team: 当前需要获取详情的team
        :param handler_param: 请求中参数
        :return:
        """
        data = ObjectDict()
        team_config = COMPANY_CONFIG.get(user.company.id).team_config
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds={'user_id': user.sysuser.id, 'company_id': company.id},
            fields=['id', 'company_id'])

        # 根据母公司，子公司区分对待，获取对应的职位信息，其他团队信息
        position_fields = 'id title status city team_id \
                           salary_bottom salary_top'.split()
        if company.id != user.company.id:
            company_positions = yield self._get_sub_company_positions(
                company.id, position_fields)

            team_positions, team_members = \
                yield self._get_team_position_members(team, company_positions)

            team_id_list = list(set([p.team_id for p in company_positions
                                     if p.team_id != team.id]))
            other_teams = yield self._get_sub_company_teams(
                self, company_id=None, team_ids=team_id_list)
        else:
            company_positions = yield self.job_position_ds.get_positions_list(
                conds={'company_id': company.id}, fields=position_fields)

            team_positions, team_members = \
                yield self._get_team_position_members(team, company_positions)

            other_teams = yield self.hr_team_ds.get_team_list(
                conds={'id': [team.id, '<>']})

        member_media_ids = [m.headimg_id for m in team_members] + \
            team_config.get(team.id) if team_config \
            else sum([[m.headimg_id, m.media_id] for m in team_members], [])

        media_id_list = [team.media_id] + member_media_ids + \
            [t.media_id for t in other_teams]
        media_dict = yield self.hr_media_ds.get_media_by_ids(media_id_list)

        # 拼装模板数据
        data.header = temp_date_tool.make_header(company, True, team)
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO})
        data.templates = temp_date_tool.make_team_detail_template(
            team, media_dict, team_members, team_positions[0:3],
            other_teams, handler_param, bool(vst_cmpy), team_config)
        data.templates_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_all_team_members(self, team_id_list):
        """
        根据团队id信息，获取所有团队，所有成员
        :param team_id_list:
        :return: {
            'all_headimg_list': [hr_meida_1, hr_meida_2],
            'all_media_list': [hr_meida_3, hr_meida_4],
            team_id_1: [hr_team_member_1, ]
            team_id_2: [hr_team_member_2, ]
        }
        """
        if not team_id_list:
            member_list = []
        else:
            member_list = yield self.hr_team_member_ds.get_team_member_list(
                conds='team_id in {}'.format(tuple(
                    team_id_list)).replace(',)', ')'))

        result = {'all_headimg_list': [], 'all_media_list': []}
        for member in member_list:
            result['all_headimg_list'].append(member.headimg_id)
            result['all_media_list'].append(member.media_id)
            if result.get(member.team_id):
                result[member.team_id].append(member)
            else:
                result[member.team_id] = [member]

        for tid in team_id_list:
            if tid not in result.keys():
                result[tid] = []

        raise gen.Return(result)

    @gen.coroutine
    def _get_team_position_members(self, team, company_positions):
        team_positions = [pos for pos in company_positions
                          if pos.team_id == team.id and pos.status == 0]
        team_members = yield self.hr_team_member_ds.get_team_member_list(
            conds={'team_id': team.id})

        raise gen.Return(team_positions, team_members)

    @gen.coroutine
    def _get_sub_company_positions(self, company_id, fields=None):
        publishers = yield self.hr_company_account_ds.get_company_accounts_list(
            conds={'company_id': company_id})
        if not publishers:
            company_positions = []
        else:
            company_positions = yield self.job_position_ds.get_positions_list(
                conds='publisher in {}'.format(tuple(
                    [p.account_id for p in publishers])).replace(',)', ')'),
                fields=fields)

        raise gen.Return(company_positions)

    @gen.coroutine
    def _get_sub_company_teams(self, company_id, team_ids=None):
        """
        获取团队信息
        当只给定company_id，通过position信息中team_id寻找出所有相关团队
        当给定team_ids时获取所有对应的团队
        :param self:
        :param company_id:
        :param team_ids:
        :return: [object_of_hr_team, ...]
        """
        if team_ids is None:
            publishers = yield self.hr_company_account_ds.get_company_accounts_list(
                conds={'company_id': company_id}, fields=None)
            publisher_id_tuple = tuple([p.account_id for p in publishers])

            if not publisher_id_tuple:
                raise gen.Return([])

            team_ids = yield self.job_position_ds.get_positions_list(
                conds='publisher in {}'.format(publisher_id_tuple).replace(',)', ')'),
                fields=['team_id'], options=['DISTINCT'])
            team_id_tuple = tuple([t.team_id for t in team_ids])
        else:
            team_id_tuple = tuple(team_ids)

        if not team_id_tuple:
            gen.Return([])
        teams = yield self.hr_team_ds.get_team_list(
            conds='id in {}'.format(team_id_tuple).replace(',)', ')'))

        raise gen.Return(teams)
