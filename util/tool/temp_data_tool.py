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
import operator

from conf.path import POSITION_PATH
from conf.platform import MEDIA_TYPE
from util.common import ObjectDict
from util.tool.str_tool import gen_salary
from util.tool.url_tool import make_static_url, make_url


def make_up_for_missing_res(res):
    if res is None:
        res = ObjectDict(res_url="", res_type=0)
    return res


def template1(sub_type, title, data, more_link=None, expandable=False):
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
        'more_link': more_link,
        'expandable': expandable
    })


def template1_data(resource, member_list=None):
    resource = make_up_for_missing_res(resource)
    return {
        'sub_title': resource.sub_title,
        'longtext': resource.longtexts,
        'clip_attrs': resource.res_attrs,
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
        'sub_title': resource.sub_title,
        'description': resource.longtexts,
        'clip_attrs': resource.res_attrs,
        'media_url': make_static_url(resource.media_url),
        'media_type': MEDIA_TYPE[resource.media_type]
    } for resource in resource_list]


def template3(title, resource_list, handler_params):
    return ObjectDict({
        'type': 3,
        'title': title,
        'data': [{
            'title': position.title,  # '文案'
            'link': make_url("/m/position/{}".format(position.id), handler_params,
                             escape=['recom', 'psc']),  # JD连接
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
            'sub_title': resource.sub_title,
            'media_url': make_static_url(resource.media_url),
            'clip_attrs': resource.res_attrs,
            'link': resource.link
        } for resource in resource_list]
    else:
        data = None

    return data


def template5(resource=None):
    return ObjectDict({'type': 5, 'title': '', 'data': resource})


def template50(resource):
    try:
        d = json.loads(resource.attrs)
    except:
        d = []
    return ObjectDict({
        'type': 50, 'title': 'map',
        'data': d
    })


def template51(resource):
    return ObjectDict({
        'type': 51, 'title': 'address',
        'data': [{
            'company_name': resource.company_name,
            'media_url': make_static_url(resource.media_url)
            if resource.media_url else '',
        }]
    })


def make_header(locale, company, team_index=False, team=None, **extra):
    if team:
        name = team.name
        description = team.slogan
    else:
        if team_index:
            name = locale.translate("company_our_teams").format(
                locale.translate(
                    extra.get("teamname_custom"),
                    plural_message=extra.get("teamname_custom"),
                    count=2))
        else:
            name = company.abbreviation or company.name
        description = '' if team_index else company.slogan

    return ObjectDict({
        'type': 'team' if team_index else 'company',
        'name': name,
        'description': description,
        'icon': make_static_url(company.logo),
        'banner': company.banner[0] if company.banner else ""
        if company.banner else None,
    })


# 团队列表模板和生成器
def make_team_member(member, head_img):
    head_img = make_up_for_missing_res(head_img)
    return ObjectDict({
        'icon': make_static_url(head_img.res_url),
        'name': member.name,
        'title': member.title,
        'description': member.description,
        'orders': member.orders
    })


def make_team_index_template(team, team_resource, more_link, member_list):
    team_resource = make_up_for_missing_res(team_resource)
    data = [{
        # 'sub_title': team.name, # 在团队列表页面,小标题就是团队名称,重复了,且hr端控制不了,=>不显示了
        'longtext': team.description,
        'media_url': make_static_url(team_resource.res_url),
        'media_type': MEDIA_TYPE[team_resource.res_type],
        'member_list': member_list,
        'clip_attrs': team.res_attrs,
    }]

    return template1(sub_type='middle', title=team.name,
                     more_link=more_link, data=data, expandable=True)


# 团队详情模版生成器
def make_introduction(member, res):
    return {
        'icon': make_static_url(res.res_url) if res else '',
        'name': member.name,
        'title': member.title,
        'description': member.description,
        'orders': member.orders
    }


def make_interview(media, res):
    return {
        'sub_title': media.sub_title,
        'longtext': '{}\n'.format(media.longtexts),
        'media_url': make_static_url(res.res_url) if res else '',
        'media_type': MEDIA_TYPE[res.res_type if res else 0],
        'clip_attrs': media.res_attrs
    }


def make_other_team_data(team, res, handler_params):
    res = make_up_for_missing_res(res)
    return {
        'sub_title': team.name,
        'link': make_url('/m/company/team/{}'.format(team.id), handler_params),
        'description': team.slogan,
        'media_url': make_static_url(res.res_url if MEDIA_TYPE[res.res_type] == "image" else res.cover),
        'media_type': MEDIA_TYPE[res.res_type],
        'clip_attrs': team.res_attrs
    }


def make_team_detail_template(locale, team, members, templates, positions,
                              other_teams, res_dic, handler_params, teamname_custom=None):
    template = []
    teamname_field = teamname_custom["teamname_custom"] if teamname_custom else '团队'

    # 无素材不显示团队
    if team.res_id:
        team_res = make_up_for_missing_res(res_dic.get(team.res_id))
        template.append(
            template1(
                sub_type='full',
                title=locale.translate('company_team_intro').format(teamname_field),
                data=[{
                    'sub_title': '',
                    'longtext': team.description,
                    'media_url': make_static_url(team_res.res_url),
                    'media_type': MEDIA_TYPE[team_res.res_type],
                    'member_list': [make_introduction(m, res_dic.get(m.res_id))
                                    for m in members],
                    'clip_attrs': team.res_attrs
                }]
            )
        )
    if templates:
        template.extend(templates)

    # 适应没有数据不显示模板块
    if positions:
        template.append(template3(
            locale.translate("team_team_is_hiring").format(teamname_field),
            positions, handler_params))

    if other_teams:
        template.append(template4(
            sub_type=0,
            title=locale.translate('company_other_text').format(
                locale.translate(teamname_field,
                                 plural_message=teamname_field,
                                 count=2)),
            data=[
                make_other_team_data(
                    team=t,
                    res=res_dic.get(t.res_id),
                    handler_params=handler_params
                ) for t in other_teams
            ])
        )

    return template


# company main page template generator
def make_company_working_env(media_list):
    return template1(sub_type='less', title=media_list[0].title,
                     data=[template1_data(media) for media in media_list])


def make_company_figure(media_list):
    return template2(title='template 2', data=template2_data(media_list))


def make_company_members(media_list):
    return template1(sub_type='less', title=media_list[0].title,
                     data=[template1_data(media) for media in media_list])


def make_company_events(media_list):
    return template4(sub_type=0, title=media_list[0].title,
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


# hr3.4
def make_company_module_type_1(media_list, module_name, more_link=""):
    """
    PRD A模块
    :param media_list:
    :param module_name:
    :return:
    """
    # 还有一个链接没有处理
    return template1(sub_type='less', title=module_name, more_link=more_link,
                     data=[template1_data(media) for media in media_list])


def make_company_module_type_2(media_list, module_name, more_link=""):
    """
    PRD B模块 - 团队列表页团队样式
    大图 小标题 描述 来自media_list[0], 参考team
    下面小图来自media_list[1:], 参考member_list
    :param media_list:
    :param module_name:
    :return:
    """
    big_one = media_list[0]
    small_ones = media_list[1:]
    member_list = []
    if small_ones:
        member_list = [ObjectDict({
            "icon": make_static_url(m.media_url),
            "name": "",
            "title": "",
            "description": ""
        }) for m in small_ones]
    data = [{
        'sub_title': big_one.sub_title,
        'longtext': big_one.longtexts,
        'clip_attrs': big_one.res_attrs,
        'media_url': make_static_url(big_one.media_url),
        'media_type': MEDIA_TYPE[big_one.media_type],
        'member_list': member_list
    }]
    return template1(sub_type='middle', title=module_name, data=data)


def make_company_module_type_3(media_list, module_name, more_link=""):
    """
    PRD C模块
    团队详情页样式
    :param media_list:
    :param module_name:
    :return:
    """
    big_one = media_list[0]
    small_ones = media_list[1:]
    member_list = []
    if small_ones:
        member_list = [ObjectDict({
            "icon": make_static_url(m.media_url),
            "name": m.sub_title,
            "title": m.title,
            "description": m.longtexts
        }) for m in small_ones]
    data = [{
        'sub_title': big_one.sub_title,
        'longtext': big_one.longtexts,
        'clip_attrs': big_one.res_attrs,
        'media_url': make_static_url(big_one.media_url),
        'media_type': MEDIA_TYPE[big_one.media_type],
        'member_list': member_list
    }]
    return template1(sub_type='full', title=module_name, data=data)


def make_company_module_type_4(media_list, module_name, module_link=""):
    """
    PRD D模块
    CEO寄语样式, module_name没有作用
    :param media_list:
    :param module_name:
    :return:
    """
    return template2(title='template 2', data=template2_data(media_list))


def make_company_module_type_5(media_list, module_name, module_link=""):
    """
    PRD E模块
    公司大事件样式
    :param media_list:
    :param module_name:
    :return:
    """
    return template4(sub_type=0, title=module_name, data=template4_data(media_list, 0))


def make_company_module_type_6(media_list, module_name, module_link=""):
    """
    地图样式, 没有module_name
    :param media_list:
    :param module_name:
    :return:
    """
    if media_list:
        return template50(resource=media_list[0])


def make_company_module_type_7(media_list, module_name, module_link=""):
    """
    二维码样式, 没有module_name
    :param media_list:
    :param module_name:
    :return:
    """
    media = ObjectDict({'media_url': '', 'company_name': ''}) \
        if not media_list else media_list[0]
    return template51(media)


def make_company_module_type_10(media_list, module_name, module_link=""):
    """
    survey样式, 没有module_name
    :param media_list:
    :param module_name:
    :return:
    """
    return template5(media_list)


# JD page
def make_position_detail_cms(media_list, res_dict, module_name, module_link):
    return template1(
        sub_type='less',
        title=module_name,
        more_link=module_link,
        data=[{
            'sub_title': m.sub_title,
            'longtext': '{}\n'.format(m.longtexts),
            'clip_attrs': m.res_attrs,
            'media_url': make_static_url(res_dict.get(m.res_id).res_url),
            'media_type': MEDIA_TYPE[res_dict.get(m.res_id).res_type]
        } for m in media_list]
    )


def make_team(team, resources, more_link, team_members, teamname_custom, locale=None):
    team_res = make_up_for_missing_res(resources.get(team.res_id))
    return template1(
        sub_type='middle',
        title='The Team' if locale and locale.code == 'en_US' else '所属' + teamname_custom["teamname_custom"],
        data=[{
            'sub_title': team.name,
            'longtext': team.description,
            'media_url': make_static_url(team_res.res_url),
            'clip_attrs': team.res_attrs,
            'media_type': MEDIA_TYPE[team_res.res_type],
            'member_list': [make_team_member(m, resources.get(m.res_id))
                            for m in team_members],
        }],
        more_link=more_link
    )
