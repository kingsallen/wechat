# coding=utf-8

# Copyright 2016 MoSeeker

"""
:author 马超（machao@moseeker.com）
:date 2016.11.18

模版分类及用途
 template 1:  'TemplateComplex'        最为复杂页面模版，团队详情页面中团队介绍
 template 2:  'TemplateFigure'         人物介绍，企业代表人物介绍
 template 3:  'TemplatePositionList'   职位列表模版
 template 4:  'TemplateLinkList'       连接列表
 template 5:  'TemplateSurvey'         调查问卷模版
 template 50: 'TemplateMap'            地图模版

"""
import json

from util.common import ObjectDict
from util.tool.url_tool import make_static_url, make_url
from util.tool.str_tool import gen_salary
from conf.platform import MEDIA_TYPE


def template1(sub_type, title, data, more_link=None):
    """

    :param sub_type:
    :param title:
    :param data:
    :param more_link:
    :return:ObjectDict({
        'type': 1,
        'sub_type': sub_type,
        'title': title,
        'more_link': more_link
        'data': [{
            'title': resource.title,
            'longtext': resource.longtext,
            'media_url': resource.media_url,
            'media_type': MEDIA_TYPE'image',
            'member_list':[{
                "icon": 'https://cdn.moseeker.com/upload/company_profile/qx/neo.jpeg',
                "name": 'Neo',
                "title": '设计师',
                "description": '我是一个乐观开朗、正气十足的非典型设计师，喜欢篮球。'
            }, ...]
        }, ....]
    })
    """
    return ObjectDict({
        'type': 1,
        'sub_type': sub_type,
        'title': title,
        'data': data,
        'more_link': more_link
    })


def template1_data(resource, member_list=None):
    return {
        'title': resource.title,
        'longtext': resource.longtext,
        'media_url': make_static_url(resource.media_url),
        'media_type': MEDIA_TYPE[resource.media_type],
        'member_list': member_list
    }


def template1_data_member(resource_list):
    return [{
        "icon": make_static_url(resource.media_url),
        "name": resource.name,
        "title": resource.itle,
        "description": resource.description,
    } for resource in resource_list]


def template2(title, data):
    return ObjectDict({
        'type': 2,
        'title': title,
        'data': data
    })


def template2_data(resource_list):
    return [{
        'title': resource.title,
        'description': resource.longtext,
        'media_url': make_static_url(resource.media_url),
        'media_type': MEDIA_TYPE[resource.media_type]
    } for resource in resource_list]


def template3(title, resource_list, handler_params):
    return ObjectDict({
        'type': 3,
        'title': title,
        'data': [{
            'title': position.title,  # '文案'
            'link': make_url('/m/position/{}'.format(position.id), handler_params),  # JD连接
            'location': position.city,  # '上海
            'salary': gen_salary(position.salary_top, position.salary_bottom)  # '5k-8k'
        } for position in resource_list]
    })


def template4(sub_type, title, data):
    return ObjectDict({
        'type': 4,
        'sub_type': sub_type,
        'title': title,
        'data': data
    })


def template4_data(resource_list, sub_type):
    if sub_type == 0:
        data = template2_data(resource_list)
    elif sub_type == 1:
        data = [{
            'title': resource.title,
            'media_url': make_static_url(resource.media_url),
            'link': resource.link
        } for resource in resource_list]
    else:
        data = None

    return data


def template5(resource=None):
    return ObjectDict({'type': 5, 'title': '', 'data': resource})


def template50(resource):
    return ObjectDict({
        'type': 50, 'title': 'address',
        'data': [eval(resource.attrs)]
    })


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


# 团队列表模板和生成器
def make_team_member(member, headimg):
    return ObjectDict({
        'icon': make_static_url(headimg.media_url),
        'name': member.name,
        'title': member.title,
        'description': member.description,
    })


def make_team_index_template(team, team_medium, more_link, member_list):
    data = {
        'title': team.name,
        'longtext': team.description,
        'media_url': make_static_url(team_medium.media_url),
        'media_type': MEDIA_TYPE[team_medium.media_type],
        'member_list': member_list
    }

    return template1(sub_type='middle', title=team.name,
                     more_link=more_link, data=data)


# 团队详情模版生成器
def make_introduction(member, headimg):
    return {
        'icon': make_static_url(headimg.media_url),
        'name': member.name,
        'title': member.title,
        'description': member.description
    }


def make_interview(member, media):
    return {
            'title': member.name,
            'longtext': '{}\n'.format(member.title),
            'media_url': make_static_url(media.media_url),
            'media_type': MEDIA_TYPE[media.media_type]
    }


def make_other_team_data(team, media, handler_params):
    return {
        'title': team.name,
        'link': make_url('/m/company/team/{}'.format(team.id), handler_params),
        'description': team.summary,
        'media_url': make_static_url(media.media_url),
        'media_type': MEDIA_TYPE[media.media_type]
    }


def make_team_detail_template(team, media_dict, members, positions,
                              other_teams, handler_params, vst_cmpy=False):
    team_media = media_dict.get(team.media_id)
    introduction, interview = [], []
    for member in members:
        introduction.append(make_introduction(
            member, media_dict.get(member.headimg_id)))
        if member.media_id:
            interview.append(make_interview(
                member, media_dict.get(member.media_id)))

    template = [
        template1(
            sub_type='full', title='团队介绍',
            data=[{
                'title': '',
                'longtext': team.description,
                'media_url': make_static_url(team_media.media_url),
                'media_type': MEDIA_TYPE[team_media.media_type],
                'member_list': introduction,
            }]
        ),
        template1(sub_type='less', title='成员采访', data=interview),
        template3('团队在招职位', positions, handler_params)
    ]
    if vst_cmpy:
        template.append(template5())
    template.append(template4(
        sub_type=0, title='其他团队',
        data=[make_other_team_data(
            team=t, media=media_dict.get(t.media_id),
            handler_params=handler_params) for t in other_teams
        ])
    )

    return template


# company main page template generator
def make_company_working_env(media_list):
    return template1(sub_type='less', title='办公环境',
                     data=[template1_data(media) for media in media_list])


def make_company_figure(media_list):
    return template2(title='template 2', data=template2_data(media_list))


def make_company_members(media_list):
    return template1(sub_type='less', title='在这里工作的人们',
                     data=[template1_data(media) for media in media_list])


def make_company_events(media_list):
    return template4(sub_type=0, title='公司大事件',
                     data=template4_data(media_list, 0))


def make_company_address(media_list):
    if media_list:
        return template50(resource=media_list[0])


def make_company_survey(media=None):
    return template5(media)


def make_company_team(resource_list, link):
    return template1(sub_type='less', title='我们的团队', more_link=link,
                     data=[template1_data(res) for res in resource_list])


# JD page
def make_mate(media_list):
    return template1(
        sub_type='less', title=media_list[0].title,
        data=[{
            'title': media.sub_title,
            'longtext': '{}\n'.format(media.longtext),
            'media_url': make_static_url(media.media_url),
            'media_type': MEDIA_TYPE[media.media_type]
        } for media in media_list]
    )


def make_team(team, team_medium):
    return template1(
        sub_type='full', title='所属团队',
        data=[{
            'title': '',
            'longtext': team.description,
            'media_url': make_static_url(team_medium.media_url),
            'media_type': MEDIA_TYPE[team_medium.media_type],
            'member_list': None,
        }]
    )
