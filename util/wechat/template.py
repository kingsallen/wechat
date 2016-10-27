# coding=utf-8

import tornado.gen as gen
import conf.common as const
from datetime import datetime
import ujson

from util.wechat.core import messager


def _make_json_data(first, keyword1=None, keyword2=None, keyword3=None,
                    keyword4=None, remark=None, colors=None):
    """
    构造发送消息模板的内容 json
    colors 可选，如果需要自定义 color，需要传入一个 dict
    """
    colors = colors or {
        "default": "#173177"
    }

    json_data = {
        "first": {"value": first or "",
                  "color": colors.get("first", colors['default'])},
    }
    if keyword1:
        json_data.update({
            "keyword1": {"value": keyword1 or "",
                         "color": colors.get("keyword1", colors['default'])}
        })
    if keyword2:
        json_data.update({
            "keyword2": {"value": keyword2 or "",
                         "color": colors.get("keyword2", colors['default'])}
        })
    if keyword3:
        json_data.update({
            "keyword3": {"value": keyword3 or "",
                         "color": colors.get("keyword3", colors['default'])}
        })

    if keyword4:
        json_data.update({
            "keyword4": {"value": keyword4 or "",
                         "color": colors.get("keyword4", colors['default'])}
        })

    if remark:
        json_data.update({
            "remark": {"value": remark or "",
                       "color": colors.get("remark", colors['default'])}
        })

    json_data = ujson.dumps(json_data, ensuer_ascii=False)
    return json_data


@gen.coroutine
def rp_binding_success_notice_tpl(
    wechat_id, openid, link, company_name,
    sys_template_id=const.TEMPLATES.RP_EMPLOYEE_BINDING):

    first = "您好！您的员工认证申请已有结果"
    keyword1 = "已通过"
    keyword2 = "员工认证"
    keyword3 = company_name
    d = datetime.now()
    keyword4 = "{}年{}月{}日{:0>2}:{:0>2} ".format(
        d.year, d.month, d.day, d.hour, d.minute)
    remark = "欢迎您成为我们的一员！请点击查看详情"

    json_data = _make_json_data(first, keyword1, keyword2, keyword3, keyword4,
                                remark)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_recom_success_notice_tpl(
    wechat_id, openid, link, company_name, recomee_name, position_title,
    sys_template_id=const.TEMPLATES.RP_RECOM):

    first = "您已成功推荐{}！感谢您对公司人才招聘的支持！".format(recomee_name)
    keyword1 = company_name
    keyword2 = position_title
    keyword3 = "已推荐"
    remark = "请点击查看详情"

    json_data = _make_json_data(first, keyword1, keyword2, keyword3, remark)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_transfer_click_success_notice_tpl(
    wechat_id, openid, link,
    nickname, position_title, sys_template_id=const.TEMPLATES.RP_SHARE):

    first = "您好，您转发的职位已被您的好友浏览"
    keyword1 = nickname
    keyword2 = position_title
    keyword3 = "面议"
    d = datetime.now()
    keyword4 = "{}年{}月{}日{:0>2}:{:0>2} ".format(
        d.year, d.month, d.day, d.hour, d.minute)
    remark = "请点击查看详情"

    json_data = _make_json_data(first, keyword1, keyword2, keyword3, keyword4,
                                remark)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)


@gen.coroutine
def rp_transfer_apply_success_notice_tpl(
    wechat_id, openid, link,
    nickname, position_title, sys_template_id=const.TEMPLATES.RP_SHARE):

    first = "您好，你转发的职位有人投递啦！"
    keyword1 = nickname
    keyword2 = position_title
    keyword3 = "面议"
    d = datetime.now()
    keyword4 = "{}年{}月{}日{:0>2}:{:0>2} ".format(
        d.year, d.month, d.day, d.hour, d.minute)
    remark = "请点击查看详情"

    json_data = _make_json_data(first, keyword1, keyword2, keyword3, keyword4,
                                remark)

    ret = yield messager.send_template(
        wechat_id, openid, sys_template_id, link, json_data, qx_retry=True)

    raise gen.Return(ret)

