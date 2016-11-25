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
from util.tool import ps_tool
from util.tool.url_tool import make_url
from conf import path


class TeamPageService(PageService):

    @gen.coroutine
    def get_sub_company(self, sub_company_id):
        sub_company = yield self.hr_company_ds.get_company(
            conds={'id': sub_company_id})

        raise gen.Return(sub_company)

    def get_team_by_id(self, team_id):
        team = yield self.hr_team_ds.get_team(conds={'id': team_id})

        raise gen.Return(team)

    @gen.coroutine
    def get_team_index(self, company, handler_params, sub_flag=False):
        data = ObjectDict(templates=[])

        if sub_flag:
            teams = yield ps_tool.get_sub_company_teams(self, company.id)
        else:
            teams = yield self.hr_team_ds.get_team_list(
                conds={'company_id': company.id})

        team_media_dict = yield ps_tool.get_media_by_ids(
            self, [t.media_id for t in teams])
        all_members_dict = yield self._get_all_team_members(
            [t.id for t in teams])
        all_member_headimg_dict = yield ps_tool.get_media_by_ids(
            self, all_members_dict.get('all_headimg_list'))

        data.header = temp_date_tool.make_header(company, team_flag=True)
        data.templates = [temp_date_tool.make_team_index_template(
            team=t, team_medium=team_media_dict.get(t.media_id),
            more_link=make_url(path.TEAM_PATH.format(t.id, handler_params)),
            member_list=[temp_date_tool.make_team_member(
                m, all_member_headimg_dict.get(m.headimg_id)) for
                m in all_members_dict.get(t.id)]
        ) for t in teams]
        data.template_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def get_team_detail(self, user, company, team, handler_params):
        data = ObjectDict()
        publishers = yield self.hr_company_account_ds.get_company_accounts_list(
            conds={'company_id': company.id})
        company_positions = yield self.job_postion_ds.get_positions_list(
            conds='publisher in {}'.format(
                tuple([p.account_id for p in publishers])))
        vst_cmpy = yield self.user_company_visit_req_ds.get_visit_cmpy(
            conds={'user_id': user.id, 'company_id': company.id},
            fields=['id', 'company_id'])

        team_positions = [pos for pos in company_positions
                          if pos.team_id == team.id and pos.status == 0]
        team_members = yield self.hr_team_member_ds.get_team_member_list(
                            conds={'team_id': team.id})
        if company.id != user.company.id:
            team_id_list = list(set([p.team_id for p in company_positions
                                     if p.team_id != team.id]))
            other_teams = yield ps_tool.get_sub_company_teams(
                self, company_id=None, team_ids=team_id_list)
        else:
            other_teams = yield self.hr_team_ds.get_team_list(
                conds={'company_id': [company.id, '<', company.id, '>']})
        media_id_list = [team.media_id] + \
            sum([[m.headimg_id, m.media_id] for m in team_members], []) + \
            [t.media_id for t in other_teams]
        media_dict = yield ps_tool.get_media_by_ids(self, media_id_list)

        data.header = temp_date_tool.make_header(company, True, team)
        data.relation = ObjectDict({
            'want_visit': self.constant.YES if vst_cmpy else self.constant.NO})
        data.templates = temp_date_tool.make_team_detail_template(
            team, media_dict, team_members, team_positions[0:3],
            other_teams, handler_params, bool(vst_cmpy))
        data.templates_total = len(data.templates)

        raise gen.Return(data)

    @gen.coroutine
    def _get_all_team_members(self, team_id_list):
        member_list = yield self.hr_team_member_ds.get_team_member_list(
            conds='id in {}'.format(tuple([t.team_id for t in team_id_list]))
        )
        result = {'all_member_id_list': []}
        for member in member_list:
            result['all_headimg_list'].append(member.headimg_id)
            result['all_media_list'].append(member.media_id)
            team_member_list = result.get(member.team_id, [])
            team_member_list.append(member)
            result[member.team_id] = team_id_list

        raise gen.Return(result)
