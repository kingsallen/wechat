# coding=utf-8

# Copyright 2016 MoSeeker

import re
import ujson
import tornado.gen as gen
import conf.common as const

from datetime import datetime, timedelta
from util.wechat.core import messager
from util.common import ObjectDict

def _make_json_data(first, remark=None, colors=None, **kwargs):
    """
    构造发送消息模板的内容 json

    :param colors: 形如{'first': '#173177'}字典
    :param kwargs: 只接受名为 keyword1 --- keyword5 的参数
    :return: json data
    """
    default = {"default": "#173177"}
    colors = dict(colors, **default) if isinstance(colors, dict) else default

    json_data = {
        "first": {"value": first or "",
                  "color": colors.get("first", colors["default"])},
    }
    for key, value in kwargs.items():
        if re.match('^keyword[1-5]$', key):
            json_data.update({
                key: {"value": value,
                      "color": colors.get(key, colors["default"])}
            })
        else:
            raise Exception('_make_json_data wrong keywords {}.'.format(key))

    if remark:
        json_data.update({
            "remark": {"value": remark,
                       "color": colors.get("remark", colors["default"])}
        })

    json_data = ujson.dumps(json_data, ensure_ascii=False)
    return json_data

@gen.coroutine
def rp_binding_success_notice_tpl(wechat_id, openid, link, company_name,
                        sys_template_id=const.TEMPLATES.RP_EMPLOYEE_BINDING):

    d = datetime.now()
    json_data = _make_json_data(
        first="您好！您的员工认证申请已有结果",
        remark="欢迎您成为我们的一员！请点击查看详情",
        keyword1="已通过",
        keyword2="员工认证",
        keyword3=company_name,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                       d.hour, d.minute))

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)

@gen.coroutine
def rp_recom_success_notice_tpl(wechat_id, openid, link, company_name,
    recomee_name, position_title, sys_template_id=const.TEMPLATES.RP_RECOM):

    json_data = _make_json_data(
        first="您已成功推荐{}！感谢您对公司人才招聘的支持！".format(recomee_name),
        remark="请点击查看详情",
        keyword1=company_name,
        keyword2=position_title,
        keyword3="已推荐")

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)

@gen.coroutine
def rp_transfer_click_success_notice_tpl(wechat_id, openid, link, nickname,
                    position_title, sys_template_id=const.TEMPLATES.RP_SHARE):

    d = datetime.now()
    json_data = _make_json_data(
        first="您好，您转发的职位已被您的好友浏览",
        remark="请点击查看详情",
        keyword1=nickname,
        keyword2=position_title,
        keyword3="面议",
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                     d.hour, d.minute))

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)

@gen.coroutine
def rp_transfer_apply_success_notice_tpl(wechat_id, openid, link, nickname,
                    position_title, sys_template_id=const.TEMPLATES.RP_SHARE):

    d = datetime.now()
    json_data = _make_json_data(
        first="您好，你转发的职位有人投递啦！",
        remark="请点击查看详情",
        keyword1=nickname,
        keyword2=position_title,
        keyword3="面议",
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                     d.hour, d.minute))

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)

@gen.coroutine
def position_view_five_notice_tpl(wechat_id, openid, link, title,
                    salary, sys_template_id=const.TEMPLATES.POSITION_VIEWED):

    """职位浏览5次，向 HR 发送消息模板"""

    d = datetime.now()
    json_data = _make_json_data(
        first="您好，您发布的职位已被浏览5次",
        remark="请点击查看详情",
        keyword1="已有5人次浏览该职位",
        keyword2=title,
        keyword3=salary,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                     d.hour, d.minute))

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=False)

    raise gen.Return(ret)

@gen.coroutine
def application_notice_to_applier_tpl(wechat_id, openid, link, job, company_name,
                                      sys_template_id=const.TEMPLATES.APPLY_NOTICE_TPL):

    """向求职者发送求职成功消息通知"""

    d = datetime.now()
    json_data = _make_json_data(
        first="感谢您抽出时间申请该职位，我们将尽快查阅您的简历",
        remark="",
        job=job,
        company=company_name,
        time="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                     d.hour, d.minute))

    send_switch = yield messager.get_send_switch(wechat_id, const.TEMPLATES_SWITCH.sys_template_id)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True, platform_switch=send_switch)

    raise gen.Return(ret)

@gen.coroutine
def application_notice_to_recommender_tpl(wechat_id, openid, link, applier_name, title,
                                          work_exp_years, lastjob, sys_template_id=const.TEMPLATES.NEW_RESUME_TPL):

    """求职者发送求职成功后，向推荐人发送消息通知"""

    json_data = _make_json_data(
        first="您好，你推荐的{}投递了简历".format(applier_name),
        remark="",
        job=title,
        resuname=applier_name,
        realname=applier_name,
        exp=work_exp_years,
        lastjob=lastjob)

    send_switch = yield messager.get_send_switch(wechat_id, const.TEMPLATES_SWITCH.sys_template_id)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=False, platform_switch=send_switch)

    raise gen.Return(ret)

@gen.coroutine
def application_notice_to_hr_tpl(wechat_id, openid, hr_name, title, applier_name,
                                          work_exp_years, lastjob, sys_template_id=const.TEMPLATES.NEW_RESUME_TPL):

    """求职者发送求职成功后，向HR发送消息通知"""

    json_data = _make_json_data(
        first="{0}，您好：\\n您刚发布的{1}职位收到了一份新简历，请及时登录hr.moseeker.com查阅并处理".format(hr_name, title),
        remark="",
        job=title,
        resuname="仟寻简历",
        realname=applier_name,
        exp=work_exp_years,
        lastjob=lastjob)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, None, json_data, qx_retry=False)

    raise gen.Return(ret)

@gen.coroutine
def favposition_notice_to_hr_tpl(wechat_id, openid, title, candidate_name, mobile,
                                          sys_template_id=const.TEMPLATES.RECOM_NOTICE_TPL):

    """用户感兴趣某职位后，向HR发送消息通知"""

    json_data = _make_json_data(
        first="您发布的“{0}”职位有了一位新候选人，请及时与TA联系".format(title),
        remark="",
        keyword1=title,
        keyword2=candidate_name,
        keyword3=mobile)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, None, json_data, qx_retry=False)

    raise gen.Return(ret)

@gen.coroutine
def favposition_notice_to_applier_tpl(company_id, title, company_name, city, user_id,
                           url, sys_template_id=const.TEMPLATES.FAVPOSITION):

    """用户感兴趣某职位后，向用户发送消息模板"""

    # 延迟2小时发送
    delay = 7200
    # 延迟消息队列消费者
    validators = 'mtp.scripts.consumer.validators.user_basic_info_not_complete'
    type = 0

    data = ObjectDict(
        first="您好, 我们对您的职业经历十分感兴趣, 希望能更了解您",
        remark="点击完善个人职业信息",
        keyword1=title,
        keyword2=company_name,
        keyword3=city)

    ret = yield messager.send_template_infra(delay, validators, sys_template_id, user_id,
                            type, company_id, url, data, enable_qx_retry=1)

    raise gen.Return(ret)

@gen.coroutine
def position_share_notice_employee_tpl(company_id, title, salary, user_id, pid,
                           url, sys_template_id=const.TEMPLATES.POSITION_VIEWED):

    """认证员工转发职位后，向员工发送转发结果消息模板"""

    # 延迟10分钟发送
    delay = 600
    # 延迟消息队列消费者
    validators = 'mtp.scripts.consumer.validators.send_viewed_template_to_employee'
    type = 0

    # 十分钟后的时间
    d = datetime.now() + timedelta(minutes=10)
    data = ObjectDict(
        first="您好，您转发的职位还没有人浏览",
        remark="多转发几个朋友或许就有浏览量了哟",
        keyword1="没有人浏览该职位",
        keyword2=title,
        keyword3=salary,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                     d.hour, d.minute),
        keyword5=pid # 作为附加字段，业务逻辑需要，微信消息模板不需要
    )

    ret = yield messager.send_template_infra(delay, validators, sys_template_id, user_id,
                            type, company_id, url, data, enable_qx_retry=1)

    raise gen.Return(ret)
