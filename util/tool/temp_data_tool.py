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
 template 51: 'TemplateQRCode'         二维码模版

"""
import json

from util.common import ObjectDict
from util.tool.url_tool import make_static_url, make_url
from util.tool.str_tool import gen_salary
from conf.platform import MEDIA_TYPE
from conf.path import POSITION_PATH


def template1(sub_type, title, data, more_link=None):
    """

    :param sub_type:
    :param title:
    :param data:
    :param more_link:
    :return:ObjectDict({
        'type': 1,
        'sub_type': sub_type,
        'title': resource.title,
        'more_link': more_link
        'data': [{
            'sub_title': resource.sub_title,
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
        'sub_title': resource.sub_title,
        'longtext': resource.longtext,
        'media_url': make_static_url(resource.media_url),
        'media_type': MEDIA_TYPE[resource.media_type],
        'member_list': member_list
    }


def template1_data_member(resource_list):
    return [{
        "icon": make_static_url(resource.media_url),
        "name": resource.name,
        "title": resource.title,
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
            'link': make_url(POSITION_PATH.format(position.id), handler_params),  # JD连接
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
        'type': 50, 'title': 'map',
        'data': eval(resource.attrs)
    })


def template51(resource):
    return ObjectDict({
        'type': 51, 'title': 'address',
        'data':  [{
            'company_name': resource.sub_title,
            'media_url': make_static_url(resource.media_url)
            if resource.media_url else '',
        }]
    })


def make_header(company, team_index=False, team=None):
    if team:
        name = team.name
        description = team.slogan
    else:
        name = '我们的团队' if team_index else company.abbreviation or company.name
        description = '' if team_index else company.slogan

    return ObjectDict({
        'type': 'team' if team_index else 'company',
        'name': name,
        'description': description,
        'icon': make_static_url(company.logo),
        'banner': make_static_url(json.loads(company.banner).get('banner0'))
        if company.banner else None,
    })


# 团队列表模板和生成器
def make_team_member(member, head_img):
    return ObjectDict({
        'icon': make_static_url(head_img.res_url),
        'name': member.name,
        'title': member.title,
        'description': member.description,
    })


def make_team_index_template(team, team_resource, more_link, member_list):
    data = [{
        'title': team.name,
        'longtext': team.summary,
        'media_url': make_static_url(team_resource.res_url),
        'media_type': MEDIA_TYPE[team_resource.res_type],
        'member_list': member_list
    }]

    return template1(sub_type='middle', title=team.name,
                     more_link=more_link, data=data)


# 团队详情模版生成器
def make_introduction(member, res):
    return {
        'icon': make_static_url(res.res_url) if res else '',
        'name': member.name,
        'title': member.title,
        'description': member.description
    }


def make_interview(media, res):
    return {
        'sub_title': media.sub_title,
        'longtext': '{}\n'.format(media.longtext),
        'media_url': make_static_url(res.res_url) if res else '',
        'media_type': MEDIA_TYPE[res.res_type if res else 0]
    }


def make_other_team_data(team, res, handler_params):
    return {
        'title': team.name,
        'link': make_url('/m/company/team/{}'.format(team.id), handler_params),
        'description': team.summary,
        'media_url': make_static_url(res.res_url),
        'media_type': MEDIA_TYPE[res.res_type]
    }


def make_team_detail_template(team, members, detail_media_list, positions,
                              other_teams, res_dic, handler_params, vst=False):
    template = []

    # 无素材不显示团队
    if team.is_show:
        template.append(
            template1(
                sub_type='full',
                title='团队介绍',
                data=[{
                    'sub_title': '',
                    'longtext': team.description,
                    'media_url': make_static_url(res_dic.get(team.res_id).res_url),
                    'media_type': MEDIA_TYPE[res_dic.get(team.res_id).res_type],
                    'member_list': [make_introduction(m, res_dic.get(m.red_id))
                                    for m in members],
                }]
            )
        )

        if detail_media_list:
            template.append(
                template1(
                    sub_type='less',
                    title=detail_media_list[0].title,
                    data=[make_interview(m, res_dic.get(m.red_id))
                          for m in detail_media_list]
                )
            )

    # 适应没有数据不显示模板块
    if positions:
        template.append(template3('团队在招职位', positions, handler_params))
    if not vst and team.is_show:
        template.append(template5())
    if other_teams:
        template.append(template4(
            sub_type=0,
            title='其他团队',
            data=[
                make_other_team_data(
                    team=t,
                    media=res_dic.get(t.res_id),
                    handler_params=handler_params
                ) for t in other_teams
            ])
        )

    return template


# company main page template generator
def make_company_working_env(media_list, resource):
    return template1(sub_type='less', title=media_list[0].title,
                     data=[template1_data(media) for media in media_list])


def make_company_figure(media_list):
    return template2(title='template 2', data=template2_data(media_list))


def make_company_members(media_list):
    return template1(sub_type='less', title=media_list[0].title,
                     data=[template1_data(media) for media in media_list])


def make_company_events(media_list):
    return template4(sub_type=0, title='公司大事件',
                     data=template4_data(media_list, 0))


def make_company_map(media_list):
    if media_list:
        return template50(resource=media_list[0])


def make_company_address(media_list):
    return template1(sub_type='less', title=media_list[0].title,
                     data=[template1_data(media) for media in media_list])


def make_company_survey(media=None):
    return template5(media)


def make_company_qr_code(media_list):
    media = ObjectDict({'media_url': '', 'company_name': ''}) \
        if not media_list else media_list[0]
    return template51(media)


def make_company_team(media_list, link=None):
    return template1(sub_type='less',
                     title=media_list[0].title,
                     more_link=link or media_list[0].link,
                     data=[template1_data(media) for media in media_list])


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
            'longtext': team.summary,
            'media_url': make_static_url(team_medium.media_url),
            'media_type': MEDIA_TYPE[team_medium.media_type],
            'member_list': None,
        }]
    )
