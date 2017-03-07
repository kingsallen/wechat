# coding=utf-8

# Copyright 2016 MoSeeker

import re
import ujson
import tornado.gen as gen
import conf.common as const

from datetime import datetime
from util.wechat.core import messager

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
def application_notice_tpl(wechat_id, openid, link, title,
                    salary, sys_template_id=const.TEMPLATES.POSITION_VIEWED):

    """职位浏览5次，向 HR 发送消息模板"""

    d = datetime.now()
    json_data = _make_json_data(
        first="感谢您抽出时间申请该职位，我们将尽快查阅您的简历",
        remark="",
        keyword1="已有5人次浏览该职位",
        keyword2=title,
        keyword3=salary,
        keyword4="{}年{}月{}日{:0>2}:{:0>2} ".format(d.year, d.month, d.day,
                                                     d.hour, d.minute))

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=False)

    raise gen.Return(ret)
