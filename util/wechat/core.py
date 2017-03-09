# coding=utf-8

import ujson

import tornado.gen as gen

import conf.common as const
import conf.wechat as wx
from setting import settings
from util.common import ObjectDict
from util.common.singleton import Singleton
from util.tool.date_tool import curr_datetime_now
from util.tool.http_tool import http_post

from app import logger
from service.data.hr.hr_wx_wechat import HrWxWechatDataService
from service.data.hr.hr_wx_notice_message import HrWxNoticeMessageDataService
from service.data.hr.hr_wx_template_message import \
    HrWxTemplateMessageDataService
from service.data.user.user_wx_user import UserWxUserDataService
from service.data.log.log_wx_message_record import \
    LogWxMessageRecordDataService


class WechatException(Exception):
    pass


class WechatNoTemplateError(WechatException):
    pass


class WechatTemplateMessager(object):

    __metaclass__ = Singleton

    def __init__(self):
        super(WechatTemplateMessager, self).__init__()
        self.logger = logger
        self.hr_wx_wechat_ds = HrWxWechatDataService()
        self.hr_wx_notice_message_ds = HrWxNoticeMessageDataService()
        self.hr_wx_template_message_ds = HrWxTemplateMessageDataService()
        self.user_wx_user_ds = UserWxUserDataService()
        self.log_wx_message_record_ds = LogWxMessageRecordDataService()

    @gen.coroutine
    def send_template(self, wechat_id, openid, sys_template_id, link,
                      json_data, qx_retry=False, link_qx=None, platform_switch=True):
        """发送消息模板到用户

        :param wechat_id: 企业号 wechat_id
        :param openid: 发送对象的企业号 open_id
        :param sys_template_id: 系统模板库 id
        :param link: 点击跳转 url,
        :param link_qx: 点击跳转的 qx url
        :param qx_retry: 失败后是否使用 qx 再次尝试发送
        :param json_data: 填充内容
        :return: 发送成功: const.YES, 发送失败:const.NO
        """

        # 获取企业号下的 template_id
        template = yield self._get_template(wechat_id, sys_template_id)

        # 获取 wechat
        wechat = yield self.hr_wx_wechat_ds.get_wechat({"id": wechat_id})

        # 企业号可选择是否开启消息模板。发送以及记录结果
        ok = False
        if platform_switch:
            ok = yield self._send_and_log(wechat, openid, template, link,
                                          json_data)

        if ok:
            raise gen.Return(const.YES)

        if qx_retry:
            # 如果需要用聚合号重试，则重复调用本方法
            qx_openid = yield self._get_qx_openid(wechat_id, openid)
            ret = yield self.send_template(settings['qx_wechat_id'],
                                           qx_openid,
                                           sys_template_id,
                                           link_qx or link,
                                           json_data,
                                           qx_retry=False)
            raise gen.Return(ret)
        else:
            raise gen.Return(const.NO)

    @gen.coroutine
    def _send(
            self,
            access_token,
            openid,
            template_id,
            link,
            topcolor,
            json_data):
        """发送模板消息例子操作

        :param access_token: 公众号的 access_token
        :param openid: 对象的 openid
        :param template_id: 公众号下的 templateid
        :param link: 点击跳转 url
        :param topcolor:
        :param json_data: 填充内容
        :return: (True/False, Response)
        """
        url = wx.API_SEND_TEMPLATE_MESSAGE % access_token
        jdata = ObjectDict()
        jdata.touser = openid
        jdata.template_id = template_id
        jdata.url = link
        jdata.topcolor = topcolor,
        jdata.data = ujson.loads(json_data)

        response = yield http_post(url, jdata, infra=False)

        ret = ObjectDict(ujson.decode(response.body))

        raise gen.Return((ret.errcode == 0, ret))

    @gen.coroutine
    def _get_template(self, wechat_id, sys_template_id):
        """根据 wechat_id, 系统模板id 获取这个 wechat 下的 template_id

        :param wechat_id: 微信 id
        :param sys_template_id: 系统模板 id
        :return: 微信下模板id
        """
        # 获取模板id
        template = yield self.hr_wx_template_message_ds.get_wx_template(
            conds={"wechat_id": wechat_id, "sys_template_id": sys_template_id})
        if not template:
            raise WechatNoTemplateError()
        raise gen.Return(template)

    @gen.coroutine
    def _save_sending_log(self, wechat, openid, template_id, link, json_data,
                          topcolor, res):
        """
        保存模板消息发送结果记录
        """
        now = curr_datetime_now()

        yield self.log_wx_message_record_ds.create_wx_message_log_record(
            fields={
                "template_id": template_id,
                "wechat_id": wechat.id,
                "msgid": res.get("msgid", 0),
                "open_id": openid,
                "url": link,
                "topcolor": topcolor,
                "jsondata": json_data,
                "errcode": res.get("errcode", -3),
                "errmsg": res.get("errmsg", ""),
                "sendtime": now,
                "updatetime": now,
                "sendtype": const.WX_MESSAGE_TEMPLATE_SEND_TYPE_WEIXIN,
                "access_token": wechat.access_token
            })

    @gen.coroutine
    def _send_and_log(self, wechat, openid, template, link, json_data):
        """发送消息模板， 记录发送log"""
        ret, res = yield self._send(
            wechat.access_token, openid, template.wx_template_id, link, template.topcolor,
            json_data)

        yield self._save_sending_log(
            wechat, openid, template.sys_template_id, link, json_data,
            template.topcolor, res)
        raise gen.Return(ret)

    @gen.coroutine
    def _get_qx_openid(self, wechat_id, openid):
        """
        获取聚合号下的 openid
        :param wechat_id:
        :param openid:
        :return:
        """
        wxuser = yield self.user_wx_user_ds.get_wxuser({
            "openid": openid,
            "wechat_id": wechat_id
        })

        qx_wxuser = yield self.user_wx_user_ds.get_wxuser({
            "unionid": wxuser.unionid,
            "wechat_id": settings['qx_wechat_id']
        })

        raise gen.Return(qx_wxuser.openid)

    @gen.coroutine
    def get_send_switch(self, wechat, notice_id):
        """
        获取企业号消息模板发送开关
        :param wechat:
        :param notice_id:
        :return:
        """
        send_switch = yield self.hr_wx_notice_message_ds.get_wx_notice_message({
            "wechat_id": wechat.id,
            "notice_id": notice_id,
            "status": 1,
        })

        res = False if not send_switch else True

        raise gen.Return(res)

messager = WechatTemplateMessager()
