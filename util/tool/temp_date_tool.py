# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.18

"""
import json

from util.common import ObjectDict
from util.tool.url_tool import make_static_url, make_url


def make_header(company, team_flag=False, team=None):
    if team:
        name = team.name
        description = team.description
        icon = ''
    else:
        name = '我们的团队' if team_flag else company.abbreviation or company.name
        description = '' if team_flag else company.introduction
        icon = make_static_url(company.logo)

    return ObjectDict({
        'type': 'team' if team_flag else 'company',
        'name': name,
        'description': description,
        'icon': icon,
        'banner': make_static_url(json.loads(company.banner).get('banner0')),
    })


def make_team_index_template(handler_params, team, team_members):
    return ObjectDict({
        'type': 1,
        'sub_type': 'middle',
        'title': team.name,
        'more_link': make_url('/m/company/team/{}'.format(team.id), handler_params),
        'data': [{
            'title':       team.name,
            'longtext':    team.description,
            'media_url':   team.logo,
            'media_type':  'image',
            'member_list': [
                {
                    "icon": member.headimg,
                    "name": member.name,
                    "title": member.title,
                    "description": member.description,
                } for member in team_members
            ]
        }]
    })


def make_team_detail_template(team, team_members, positions, vst_cmpy=False):
    introduction_data, interview_data = [], []
    for member in team_members:
        introduction_data.append({
            "icon": member.icon,
            "name": member.name,
            "title": member.title,
            "description": member.description})
        interview_data.append({
            'title': member.name,
            'longtext': '{}\n'.format(member.title),
            'media_url': member.video,
            'media_type': 'video',
            'member_list': []})

    introduction = ObjectDict({
        'type': 1,
        'sub_type': 'full',
        'title': '团队介绍',
        'data': [{
            'title': '',
            'longtext': team.description,
            'media_url': team.media,
            'media_type': 'image',
            'member_list': introduction_data,
        }]
    })

    interview = ObjectDict({
        'type': 1,
        'sub_type': 'less',
        'title': '成员采访',
        'data': interview_data,
    })

    position = ObjectDict({
        'type': 3,
        'title': "团队在招职位",
        'data': [{
            "title": pos.title, # '文案'
            "link": pos.url,
            "location": pos.loaction, # '上海
            "salary": pos.salary  #'5k-8k'
        } for pos in positions]
    })

    template = [introduction, interview, position]

    if vst_cmpy:
        template.append(ObjectDict({'type': 5, 'title': '', 'data': None}))

    return template


def make_other_team(company_id, team_id):

    teams = 'get all teams' % company_id
    otherteam = ObjectDict({
        'type': 4,
        'sub_type': 0,
        'title': '其他团队',
        'data': [
            {
                "title": team.name,
                "link": team.link,
                "description": team.description,
                "media_url": team.media,
                "media_type": "image"
            } for team in teams if team.id != team_id]
    })

    return otherteam




