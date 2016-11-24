# coding: utf-8

# Copyright 2016 MoSeeker

from tornado import gen
from util.common import ObjectDict


@gen.coroutine
def get_sub_company_teams(self, company_id):
    publishers = yield self.hr_company_account_ds.get_company_accounts_list(
        conds={'company_id': company_id})
    publisher_id_tuple = tuple([p.account_id for p in publishers])
    team_ids = yield self.job_postion_ds.get_positions_list(
        conds='publisher in {}'.format(publisher_id_tuple),
        fields=['team_id'], options=['DISTINCT'])
    team_id_tuple = tuple([t.team_id for t in team_ids])
    teams = yield self.hr_team_ds.get_team_list(
        conds='id in {}'.format(team_id_tuple))

    raise gen.Return(teams)


@gen.coroutine
def get_media_by_ids(self, id_list):
    media_list = yield self.hr_media_ds.get_media_list(
        conds='id in {}'.format(tuple(id_list)))

    raise gen.Return({m.id: m for m in media_list})


@gen.coroutine
def get_team_resource(self, team_list):
    media_list = yield self.hr_media_ds.get_media_list(
        conds='id in {}'.format(tuple([t.media_id for t in team_list])))
    media_dict = {str(m.id): m for m in media_list}

    raise gen.Return([ObjectDict({
        # 'show_order': team.show_order, 如果需要对team排序
        'id': team.id,
        'title': team.name,
        'longtext': team.description,
        'media_url': media_dict.get(str(team.id).media_url),
        'media_type': media_dict.get(str(team.id).media_type),
    }) for team in team_list])


@gen.coroutine
def get_team_member_resource(self, team_id, headimgs=True, ):
    team_members = yield self.hr_team_member_ds.get_team_member_list(
        conds={'team_id': team_id})
    headimg_list = yield self.hr_media_ds.get_media_list(
        conds='id in {}'.format(tuple([m.headimg_id for m in team_members])))
    headimgs = {str(m.id): m for m in headimg_list}

    raise gen.Return([ObjectDict({
        'id': member.id,
        "icon": headimgs.get(member.headimg_id),
        "name": member.name,
        "title": member.itle,
        "description": member.description,
    }) for member in team_members])


