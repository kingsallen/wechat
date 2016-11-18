# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.18

"""
import json

from util.common import ObjectDict
from util.tool.url_tool import make_static_url, make_url


def make_header(company, team_flag=False):
    return ObjectDict({
        'type': 'team' if team_flag else 'company',
        'name': '我们的团队' if team_flag else company.abbreviation or company.name,
        'description': '' if team_flag else company.introduction,
        'icon': make_static_url(company.logo),
        'banner': make_static_url(json.loads(company.banner).get('banner0')),
    })


def make_team_index_template(hander_params, team, team_members):
    return ObjectDict({
        'type': 1,
        'sub_type': 'middle',
        'title': team.name,
        'more_link': make_url('/m/company/team/{}'.format(team.id), hander_params),
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
