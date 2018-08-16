# coding=utf-8

import ujson

import tornado.gen as gen

import conf.common as const
import conf.path as path
import conf.wechat as wx
from globals import logger
from service.data.hr.hr_wx_notice_message import HrWxNoticeMessageDataService
from service.data.hr.hr_wx_template_message import \
    HrWxTemplateMessageDataService
from service.data.hr.hr_wx_wechat import HrWxWechatDataService
from service.data.log.log_wx_message_record import \
    LogWxMessageRecordDataService
from service.data.user.user_wx_user import UserWxUserDataService
from setting import settings
from util.common import ObjectDict
from util.common.singleton import Singleton
from util.tool.date_tool import curr_datetime_now
from util.tool.http_tool import http_post, http_get
from util.tool.url_tool import make_url


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
                      json_data, qx_retry=False, platform_switch=True):
        """发送消息模板到用户

        :param wechat_id: 企业号 wechat_id
        :param openid: 发送对象的企业号 open_id
        :param sys_template_id: 系统模板库 id
        :param link: 点击跳转 url,
        :param qx_retry: 失败后是否使用 qx 再次尝试发送
        :param json_data: 填充内容
        :platform_switch: 是否发送开关
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
            self.logger.info("qx_retry: {} {} {}".format(wechat_id, openid, qx_openid))
            ret = yield self.send_template(settings['qx_wechat_id'],
                                           qx_openid,
                                           sys_template_id,
                                           link,
                                           json_data,
                                           qx_retry=False)
            raise gen.Return(ret)
        else:
            raise gen.Return(const.NO)

    @gen.coroutine
    def send_template_infra(self, delay, validators, validators_params, sys_template_id, user_id,
                            type, company_id, url, data, enable_qx_retry=0):
        """
        通过基础服务，发送消息模板到用户

        TODO 基础服务需要按send_template，升级现有的接口，支持企业号发送开关，招聘助手发送
        company_id改为 wechat_id，增加 type 类型

        :param delay: int，必填，延迟时间，单位秒
        :param validators: string，非必填，处理前的校验器, 用;分开多个, 每个校验器均返回 true 才能继续处理, 否则放弃处理
        :param validators_params: validators 需要的参数，一个 json 字符串。 validator 会对其进行解析后获取这个对象
        :param sys_template_id: int，必填，需要发送的消息模板ID，config_sys_template_message_library.id
        :param user_id: string, 必填，user_user.id
        :param type: int，非必填，用户类型，默认（包括不传递任何值）为C端用户。0 或 不传递表示C端帐号，1表示B端帐号。如果type=1是，company_id和enable_qx_retry将无效
        :param company_id: int，必填，hr_company.id 主公司的ID
        :param url: string，非必填，消息模板点击链接url
        :param data: string，必填，模板数据
        :param enable_qx_retry: int，非必填，如果企业发送失败后，是否需用使用仟寻再次发送，0:不用 1：可以
        :return: 发送成功: const.YES, 发送失败:const.NO
        """

        jdata = ObjectDict(
            delay=delay,
            validators=validators,
            validators_params=validators_params,
            sys_template_id=sys_template_id,
            user_id=user_id,
            type=type,
            company_id=company_id,
            url=url,
            data=data,
            enable_qx_retry=enable_qx_retry
        )

        res = yield http_post(path.MESSAGE_TEMPLATE, jdata)

        if res.status == const.API_SUCCESS:
            raise gen.Return(const.YES)
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
        :return: (True/False, Response Body)
        """
        url = wx.API_SEND_TEMPLATE_MESSAGE % access_token
        jdata = ObjectDict()
        jdata.touser = openid
        jdata.template_id = template_id
        jdata.url = link
        jdata.topcolor = topcolor,
        jdata.data = ujson.loads(json_data)

        res = yield http_post(url, jdata, infra=False)
        return res.errcode == 0, res

    @gen.coroutine
    def _get_template(self, wechat_id, sys_template_id):
        """根据 wechat_id, 系统模板id 获取这个 wechat 下的 template_id

        :param wechat_id: 微信 id
        :param sys_template_id: 系统模板 id
        :return: 微信下模板id
        """
        # 获取模板id
        template = yield self.hr_wx_template_message_ds.get_wx_template(
            conds={
                "wechat_id": wechat_id,
                "sys_template_id": sys_template_id,
                "disable": const.NO
            })
        if not template:
            raise WechatNoTemplateError()
        raise gen.Return(template)

    @gen.coroutine
    def _save_sending_log(self, wechat, openid, template_id, link, json_data,
                          topcolor, res):
        """
        保存模板消息发送结果记录
        """
        self.logger.info(
            "_save_sending_log: {}, {}, {}, {}, {}, {}, {}".format(wechat, openid, template_id, link, json_data,
                                                                   topcolor, res))
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
        self.logger.info("发送消息模板: {}, {}, {}, {}, {}".format(wechat, openid, template, link, json_data))
        ret, res = yield self._send(
            wechat.access_token, openid, template.wx_template_id, link, template.topcolor,
            json_data)
        self.logger.info("发送消息模板记录: {}, {}".format(ret, res))

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
        wxuser = yield self.user_wx_user_ds.get_wxuser(conds={
            "openid": openid,
            "wechat_id": wechat_id
        })

        qx_wxuser = yield self.user_wx_user_ds.get_wxuser(conds={
            "unionid": wxuser.unionid,
            "wechat_id": settings['qx_wechat_id']
        })

        raise gen.Return(qx_wxuser.openid)

    @gen.coroutine
    def get_send_switch(self, wechat_id, notice_id):
        """
        获取企业号消息模板发送开关
        :param wechat_id:
        :param notice_id:
        :return:
        """
        send_switch = yield self.hr_wx_notice_message_ds.get_wx_notice_message({
            "wechat_id": wechat_id,
            "notice_id": notice_id,
            "status": 1,
        })

        res = False if not send_switch else True

        raise gen.Return(res)


messager = WechatTemplateMessager()


# 与微信 API 之间的交互的工具方法
@gen.coroutine
def get_wxuser(access_token, openid):
    """用 openid 拉取用户信息
    https://mp.weixin.qq.com/wiki?action=doc&id=mp1421140839&t=0.8130415470934214
    :return ObjectDict
    when success
    {
       "subscribe": 1,
       "openid": "o6_bmjrPTlm6_2sgVt7hMZOPfL2M",
       "nickname": "Band",
       "sex": 1,
       "language": "zh_CN",
       "city": "广州",
       "province": "广东",
       "country": "中国",
       "headimgurl":  "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4
    eMsv84eavHiaiceqxibJxCfHe/0",
      "subscribe_time": 1382694957,
      "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
      "remark": "",
      "groupid": 0,
      "tagid_list":[128,2]
    }

    when error
    {"errcode":40003,"errmsg":" invalid openid"}
    """
    assert access_token and openid
    ret = yield http_get(wx.WX_INFO_USER_API % (access_token, openid), infra=False)
    raise gen.Return(ret)


@gen.coroutine
def get_qrcode(access_token, scene_str, action_name="QR_LIMIT_STR_SCENE"):
    """获得专属二维码
    :return url
    """
    params = ObjectDict(
        action_name=action_name,
        action_info=ObjectDict(
            scene=ObjectDict(
                scene_str=scene_str
            )
        )
    )

    ret = yield http_post(wx.WX_CREATE_QRCODE_API % access_token, params, infra=False)
    if ret:
        raise gen.Return(wx.WX_SHOWQRCODE_API % (ret.get("ticket")))
    raise gen.Return(None)


@gen.coroutine
def get_temporary_qrcode(access_token, pattern_id, action_name="QR_SCENE"):
    """
    生成带场景值的临时二维码
    :param pattern_id：场景id      1：员工认证  2：内推政策
    :param access_token
    :param action_name
    :return:
    """
    scene_id = int('11110000000000000000000000000000', base=2) + pattern_id
    params = ObjectDict({
        "expire_seconds": wx.TEMPORARY_QRCODE_EXPIRE,
        "action_name": action_name,
        "action_info": {
            "scene": {
                "scene_id": scene_id
            }
        }
    })
    ret = yield http_post(wx.WX_CREATE_QRCODE_API % access_token, params, infra=False)
    if ret:
        raise gen.Return(wx.WX_SHOWQRCODE_API % (ret.get("ticket")))
    raise gen.Return(None)


@gen.coroutine
def send_succession_message(wechat, open_id, pattern_id):
    """
    发送接续流程的信息给用户
    :param wechat:
    :param open_id:
    :param pattern_id: 1：员工认证  2：内推政策
    :return:
    """
    if pattern_id == 1:
        url = make_url(path.EMPLOYEE_REFERRAL_POLICY, wechat_signature=wechat.get("wechat_signature"))
        content = '点击完成<a href="{}">员工认证</a> <br> 更多积分奖励等你来~'.format(url)
    elif pattern_id == 2:
        url = make_url(path.EMPLOYEE_VERIFY, wechat_signature=wechat.get("wechat_signature"))
        content = '点击查看<a href="{}">内推政策</a>'.format(url)
    else:
        content = "欢迎关注：{}, 点击菜单栏发现更多精彩~".format(wechat.get("name"))
    jdata = ObjectDict({
        "touser": open_id,
        "msgtype": "text",
        "text": {
            "content": content
        }
    })
    yield http_post(
        wx.WX_CS_MESSAGE_API % wechat.get("access_token"), data=jdata, infra=False).json()
