# coding: utf-8

# Copyright 2016 MoSeeker

from tornado import gen


@gen.coroutine
def get_sub_company_teams(self, company_id, publishers=None, team_ids=None):
    """
    获取团队信息
    当只给定company_id，通过position信息中team_id寻找出所有相关团队
    当给定team_ids时获取所有对应的团队
    :param self:
    :param company_id:
    :param publishers:
    :param team_ids:
    :return: [object_of_hr_team, ...]
    """
    if not team_ids:
        if not publishers:
            publishers = yield self.hr_company_account_ds.get_company_accounts_list(
                conds={'company_id': company_id})
            publisher_id_tuple = tuple([p.account_id for p in publishers])
        else:
            publisher_id_tuple = tuple(publishers)
        team_ids = yield self.job_postion_ds.get_positions_list(
            conds='publisher in {}'.format(publisher_id_tuple),
            fields=['team_id'], options=['DISTINCT'])
        team_id_tuple = tuple([t.team_id for t in team_ids])
    else:
        team_id_tuple = tuple(team_ids)
    teams = yield self.hr_team_ds.get_team_list(
        conds='id in {}'.format(team_id_tuple))

    raise gen.Return(teams)


@gen.coroutine
def get_media_by_ids(self, id_list, list_flag=False):
    """
    获取指定media_id列表内所有media对象
    :param self:
    :param id_list:
    :param list_flag: 为真返回media列表
    :return: {object_hr_media.id: object_hr_media, ...} or [object_hr_media ...]
    """
    media_list = yield self.hr_media_ds.get_media_list(
        conds='id in {}'.format(tuple(id_list)))

    if list_flag:
        raise gen.Return(media_list)
    raise gen.Return({m.id: m for m in media_list})
