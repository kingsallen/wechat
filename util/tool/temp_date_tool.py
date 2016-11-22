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
    else:
        name = '我们的团队' if team_flag else company.abbreviation or company.name
        description = '' if team_flag else company.introduction

    return ObjectDict({
        'type': 'team' if team_flag else 'company',
        'name': name,
        'description': description,
        'icon': make_static_url(company.logo),
        'banner': make_static_url(json.loads(company.banner).get('banner0')),
    })


def make_team_member(member, headimg):
    return ObjectDict({
        "icon": headimg.media_url,
        "name": member.name,
        "title": member.title,
        "description": member.description,
    })


def make_team_index_template(handler_params, team, team_medium, member_list):
    return ObjectDict({
        'type': 1,
        'sub_type': 'middle',
        'title': team.name,
        'more_link': make_url('/m/company/team/{}'.format(team.id), handler_params),
        'data': [{
            'title':       team.name,
            'longtext':    team.description,
            'media_url':   team_medium.media_url,
            'media_type':  'image',
            'member_list': member_list
        }]
    })


def make_introduction(member, headimg):
    return {
        "icon": headimg.media_url,
        "name": member.name,
        "title": member.title,
        "description": member.description
    }


def make_interview(member, media):
    return {
            'title': member.name,
            'longtext': '{}\n'.format(member.title),
            'media_url': media.media_url,
            'media_type': 'video'
    }

def make_positon(position, handler_params):
    return {
        "title": position.title,  # '文案'
        "link": make_url('/m/position/{}'.format(position.id), handler_params),  # JD连接
        "location": position.city,  # '上海
        "salary": '{}k-{}'.format(position.salary_bottom, position.salary_top)  # '5k-8k'
    }


def make_team_detail_template(team, introduction_data, interview_data,
                              positions, vst_cmpy=False):

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
        'data': positions
    })

    template = [introduction, interview, position]

    if vst_cmpy:
        template.append(ObjectDict({'type': 5, 'title': '', 'data': None}))

    return template


def make_other_team_data(team, media, handler_params):
    return {
        "title": team.name,
        "link": make_url('/m/company/team/{}'.format(team.id), handler_params),
        "description": team.summary,
        "media_url": media.media_url,
        "media_type": "image"
    }


def make_other_team(other_teams):
    other_team = ObjectDict({
        'type': 4,
        'sub_type': 0,
        'title': '其他团队',
        'data': other_teams
    })

    return other_team




