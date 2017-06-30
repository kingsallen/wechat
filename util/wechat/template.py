# coding=utf-8

from datetime import datetime, timedelta

import tornado.gen as gen

import conf.common as const
from util.tool.json_tool import json_dumps
from util.wechat.core import messager
from util.tool.dict_tool import ObjectDict


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
def employee_refine_custom_fields_tpl(wechat_id, openid, link, company_name,
    sys_template_id=const.TEMPLATES.REFINE_EMPLOYEE_INFO_TPL):
    """员工认证自定义字段填写通知模版"""

    send_switch = yield messager.get_send_switch(
        wechat_id, const.TEMPLATES_SWITCH.REFINE_EMPLOYEE_INFO_TPL)

    d = datetime.now()
    json_data = _make_json_data(
        first="您已完成员工认证",
        remark="点击填写详细信息",
        keyword1="已认证",
        keyword2="员工认证",
        keyword3=company_name,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(
            d.year, d.month, d.day, d.hour, d.minute)
    )
    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data,
        qx_retry=True, platform_switch=send_switch)

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
def application_notice_to_applier_tpl(wechat_id, openid, link, job,
    company_name, sys_template_id=const.TEMPLATES.APPLY_NOTICE_TPL):
    """向求职者发送求职成功消息通知"""

    d = datetime.now()
    json_data = _make_json_data(
        first="感谢您抽出时间申请该职位，我们将尽快查阅您的简历",
        remark="",
        job=job,
        company=company_name,
        time="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                              d.hour, d.minute))

    send_switch = yield messager.get_send_switch(
        wechat_id, const.TEMPLATES_SWITCH.APPLY_NOTICE_TPL)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True,
        platform_switch=send_switch)

    raise gen.Return(ret)


@gen.coroutine
def application_notice_to_recommender_tpl(wechat_id, openid, link,
    applier_name, title, work_exp_years, lastjob,
    sys_template_id=const.TEMPLATES.NEW_RESUME_TPL):
    """求职者发送求职成功后，向推荐人发送消息通知"""

    json_data = _make_json_data(
        first="您好，你推荐的{}投递了简历".format(applier_name),
        remark="",
        job=title,
        resuname=applier_name,
        realname=applier_name,
        exp=work_exp_years,
        lastjob=lastjob)

    send_switch = yield messager.get_send_switch(
        wechat_id, const.TEMPLATES_SWITCH.NEW_RESUME_TPL)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=False,
        platform_switch=send_switch)

    raise gen.Return(ret)


@gen.coroutine
def application_notice_to_hr_tpl(wechat_id, openid, hr_name, title,
    applier_name, work_exp_years, lastjob,
    sys_template_id=const.TEMPLATES.NEW_RESUME_TPL):
    """求职者发送求职成功后，向HR发送消息通知"""

    json_data = _make_json_data(
        first="{0}，您好：\n您刚发布的{1}职位收到了一份新简历，请及时登录hr.moseeker.com查阅并处理".format(
            hr_name, title),
        remark="",
        job=title,
        resuname="仟寻简历",
        realname=applier_name,
        exp=work_exp_years,
        lastjob=lastjob)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, "", json_data, qx_retry=False)

    raise gen.Return(ret)


@gen.coroutine
def favposition_notice_to_hr_tpl(wechat_id, openid, title, candidate_name,
    mobile, sys_template_id=const.TEMPLATES.RECOM_NOTICE_TPL):
    """用户感兴趣某职位后，向HR发送消息通知"""

    json_data = _make_json_data(
        first="您发布的“{0}”职位有了一位新候选人，请及时与TA联系".format(title),
        remark="",
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

    # 延迟2小时发送
    delay = 7200
    # 延迟消息队列消费者
    validators = 'mtp.scripts.consumer.validators.UserBasicInfoNotCompleteValidator'
    type = 0

    validators_params_dict = ObjectDict()
    validators_params_dict.user_id = user_id,
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
    url, sys_template_id=const.TEMPLATES.POSITION_VIEWED):
    """认证员工转发职位后，向员工发送转发结果消息模板"""

    # 延迟10分钟发送
    delay = 600
    # 延迟消息队列消费者
    validators = 'mtp.scripts.consumer.validators.SendViewedTemplateToEmployeeValidator'
    type = 0
    validators_params_dict = ObjectDict()
    validators_params_dict.user_id = user_id,
    validators_params_dict.company_id = company_id
    validators_params_dict.url = url
    validators_params_dict.pid = pid
    validators_params = json_dumps(validators_params_dict)

    # 十分钟后的时间
    d = datetime.now() + timedelta(minutes=10)
    data = _make_json_data(
        first="您好，您转发的职位还没有人浏览",
        remark="多转发几个朋友或许就有浏览量了哟",
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
