# coding=utf-8

import time
from datetime import datetime, timedelta

import tornado.gen as gen

import conf.common as const
from globals import logger
from util.tool.dict_tool import ObjectDict
from util.tool.json_tool import json_dumps
from util.wechat.core import messager


def _join_suffix(link, sys_template_id):
    if "?" in link:
        link = link + const.TEMPLATE_URL_SUFFIX.format(sys_template_id, str(int(time.time() * 1000)))
    else:
        link = link + const.TEMPLATE_URL_SUFFIX_.format(sys_template_id, str(int(time.time() * 1000)))
    return link


def _make_json_data(first, remark=None, colors=None, encode=True, **kwargs):
    """
    构造发送消息模板的内容 json

    :param colors: 形如{'first': '#173177'}字典
    :param kwargs:
    :param encode: True/False 是否需要对结果进行 dumps
    :return: json/dict
    """
    default = {"default": "#173177"}
    colors = dict(colors, **default) if isinstance(colors, dict) else default

    data_dict = {
        "first": {"value": first or "",
                  "color": colors.get("first", colors["default"])},
    }
    for key, value in kwargs.items():
        data_dict.update({
            key: {"value": value,
                  "color": colors.get(key, colors["default"])}
        })

    if remark:
        data_dict.update({
            "remark": {"value": remark,
                       "color": colors.get("remark", colors["default"])}
        })

    if encode:
        return json_dumps(data_dict)
    else:
        return data_dict


@gen.coroutine
def rp_binding_success_notice_tpl(
    wechat_id, openid, link, company_name, employee_slug,
    sys_template_id=const.TEMPLATES.RP_EMPLOYEE_BINDING):
    link = _join_suffix(link, sys_template_id)
    d = datetime.now()
    json_data = _make_json_data(
        first="""# 专属刮刮卡，打开有惊喜 # 恭喜您获得员工认证奖励
        """,
        remark="请点击领取奖励",
        keyword1="已通过",
        keyword2="{}认证".format(employee_slug),
        keyword3=company_name,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day, d.hour, d.minute),
        colors={"first": "#E75E48", "remark": "#E75E48"})

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_recom_success_notice_tpl(wechat_id, openid, link, company_name,
                                recomee_name, position_title, sys_template_id=const.TEMPLATES.RP_RECOM):
    link = _join_suffix(link, sys_template_id)
    d = datetime.now()
    json_data = _make_json_data(
        first="""# 专属刮刮卡，打开有惊喜 # 恭喜您获得员工推荐奖励
        """,
        remark="请点击领取奖励",
        keyword1=recomee_name,
        keyword2=position_title,
        keyword3="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day, d.hour, d.minute),
        colors={"first": "#E75E48", "remark": "#E75E48"})

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_transfer_click_success_notice_tpl(wechat_id, openid, link, nickname,
                                         position_title, sys_template_id=const.TEMPLATES.RP_SHARE):
    link = _join_suffix(link, sys_template_id)
    d = datetime.now()
    json_data = _make_json_data(
        first="""# 专属刮刮卡，打开有惊喜 # 恭喜您获得转发职位奖励
        """,
        remark="请点击领取奖励",
        keyword1=nickname,
        keyword2=position_title,
        keyword3="面议",
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                  d.hour, d.minute),
        colors={"first": "#E75E48", "remark": "#E75E48"}
    )

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_transfer_apply_success_notice_tpl(wechat_id, openid, link, nickname,
                                         position_title, sys_template_id=const.TEMPLATES.RP_SHARE):
    link = _join_suffix(link, sys_template_id)
    d = datetime.now()
    json_data = _make_json_data(
        first="""# 专属刮刮卡，打开有惊喜 # 恭喜您获得转发职位奖励
        """,
        remark="请点击领取奖励",
        keyword1=nickname,
        keyword2=position_title,
        keyword3="面议",
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                  d.hour, d.minute),
        colors={"first": "#E75E48", "remark": "#E75E48"})

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_recom_screen_success_notice_tpl(wechat_id, openid, link, nickname,
                                       position_title, sys_template_id=const.TEMPLATES.RP_SCREEN):
    link = _join_suffix(link, sys_template_id)
    d = datetime.now()
    json_data = _make_json_data(
        first="""# 专属刮刮卡，打开有惊喜 # 恭喜您获得推荐简历通过初筛奖励
        """,
        remark="请点击领取奖励",
        keyword1=nickname,
        keyword2=position_title,
        keyword3="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                  d.hour, d.minute),
        colors={"first": "#E75E48", "remark": "#E75E48"})

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def position_view_five_notice_tpl(wechat_id, openid, link, title,
                                  salary, sys_template_id=const.TEMPLATES.POSITION_VIEWED_FIVE_TIMES, current_wechat_id=None):
    """职位浏览5次，向 HR 发送消息模板"""
    link = _join_suffix(link, sys_template_id)
    d = datetime.now()
    json_data = _make_json_data(
        first="您好，有求职者查看了你的职位",
        remark="请及时登录hr.moseeker.com查看",
        keyword1="已有5人次浏览该职位",
        keyword2=title,
        keyword3=salary,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                  d.hour, d.minute))
    # send_switch = yield messager.get_send_switch(current_wechat_id, const.TEMPLATES_SWITCH.JD_SCAN_FIVE_TIME) if current_wechat_id else True
    send_switch = True
    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=False, platform_switch=send_switch)

    raise gen.Return(ret)


@gen.coroutine
def favposition_notice_to_hr_tpl(wechat_id, openid, title, candidate_name,
                                 mobile, sys_template_id=const.TEMPLATES.RECOM_NOTICE_TPL):
    """用户感兴趣某职位后，向HR发送消息通知"""

    json_data = _make_json_data(
        first="您发布的“{0}”职位有了一位新候选人，请及时与TA联系".format(title),
        remark="请及时登录hr.moseeker.com查看",
        keyword1=title,
        keyword2=candidate_name,
        keyword3=mobile)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, "", json_data, qx_retry=False)

    raise gen.Return(ret)


@gen.coroutine
def favposition_notice_to_applier_tpl(company_id, position_info, company_name,
                                      user_id, url, sys_template_id=const.TEMPLATES.FAVPOSITION):
    """用户感兴趣某职位后，向用户发送消息模板"""
    url = _join_suffix(url, sys_template_id)
    # 延迟2小时发送
    delay = 7200
    # 延迟消息队列消费者
    validators = 'UserBasicInfoNotCompleteValidator'
    type = 0

    validators_params_dict = ObjectDict()
    validators_params_dict.user_id = user_id
    validators_params_dict.company_id = company_id
    validators_params_dict.url = url
    validators_params_dict.pid = position_info.id
    validators_params = json_dumps(validators_params_dict)

    data = _make_json_data(
        first="您好，我们对您的职业经历十分感兴趣，希望能更了解您",
        remark="点击完善个人职业信息",
        encode=False,
        keyword1=position_info.title,
        keyword2=company_name,
        keyword3=position_info.city)

    ret = yield messager.send_template_infra(
        delay=delay,
        validators=validators,
        validators_params=validators_params,
        sys_template_id=sys_template_id,
        user_id=user_id,
        type=type,
        company_id=company_id,
        url=url,
        data=data,
        enable_qx_retry=1)

    raise gen.Return(ret)


@gen.coroutine
def position_share_notice_employee_tpl(company_id, title, salary, user_id, pid,
                                       url, sys_template_id=const.TEMPLATES.POSITION_VIEWED_SHARED):
    """认证员工转发职位后，向员工发送转发结果消息模板"""
    url = _join_suffix(url, sys_template_id)
    # 延迟10分钟发送
    delay = 600
    # 延迟消息队列消费者
    validators = 'SendViewedTemplateToEmployeeValidator'
    type = 0
    validators_params_dict = ObjectDict()
    validators_params_dict.user_id = user_id
    validators_params_dict.company_id = company_id
    validators_params_dict.url = url
    validators_params_dict.pid = pid
    validators_params = json_dumps(validators_params_dict)

    # 十分钟后的时间
    d = datetime.now() + timedelta(minutes=10)
    data = _make_json_data(
        first="您好，您转发的职位在过去10分钟内已被N人浏览",
        remark="请点击领取奖励",
        encode=False,
        keyword1="没有人浏览该职位",
        keyword2=title,
        keyword3=salary,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(
            d.year, d.month, d.day, d.hour, d.minute),
    )

    ret = yield messager.send_template_infra(
        delay=delay,
        validators=validators,
        validators_params=validators_params,
        sys_template_id=sys_template_id,
        user_id=user_id,
        type=type,
        company_id=company_id,
        url=url,
        data=data,
        enable_qx_retry=1)

    raise gen.Return(ret)
