# coding=utf-8

import tornado.gen as gen
import conf.common as const
from util.tool.http_tool import http_post

from util.common import ObjectDict
from service.page.base import PageService
from util.tool.date_tool import curr_now
from setting import settings


class UserPageService(PageService):

    _USER_LOGIN_PATH = "/user/login"

    _ROUTE = ObjectDict({
        'bind_wx_mobile': 'user/wxbindmobile'
    })

    def __init__(self, logger):
        super().__init__(logger)

    @gen.coroutine
    def login_by_mobile_pwd(self, mobile, password):
        """调用基础服务接口登录

        返回：
        {
            user_id:
            unionid:
            mobile:
            last_login_time,
            name:
            headimg:
        }
        """
        ret = yield http_post(
            route=self._USER_LOGIN_PATH,
            jdata=dict(mobile=str(mobile), password=str(password)))
        raise gen.Return(ret)

    @gen.coroutine
    def create_user_user(self, userinfo, wechat_id, remote_ip, source):

        # 查询 这个 unionid 是不是已经存在
        user_record = yield self.user_user_ds.get_user({
            "unionid": userinfo.unionid
        })

        # 如果存在，返回 userid
        if user_record:
            user_id = user_record.id
        else:
            # 如果不存在，创建 user_user 记录，返回 user_id
            user_id = yield self.user_user_ds.create_user({
                "username":         userinfo.unionid,
                "password":         "",
                "register_time":    curr_now(),
                "register_ip":      remote_ip,
                "mobile":           0,
                "national_code_id": 1,
                "wechat_id":        wechat_id,
                "last_login_time":  curr_now(),
                "last_login_ip":    remote_ip,
                "login_count":      1,
                "unionid":          userinfo.unionid,
                "source":           source,
                "nickname":         userinfo.nickname,
                "name":             "",
                "headimg":          userinfo.headimgurl,
            })

            assert user_id
            yield self.user_settings_ds.create_user_settings({
                "user_id": user_id
            })

        raise gen.Return(user_id)

    @gen.coroutine
    def get_user_user_unionid(self, unionid):
        ret = yield self.user_user_ds.get_user({
            "unionid": unionid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_user_user_id(self, user_id):
        ret = yield self.user_user_ds.get_user({
            "id": user_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_openid_wechat_id(self, openid, wechat_id):
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "openid":    openid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_unionid_wechat_id(self, unionid, wechat_id):
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "unionid":   unionid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_id(self, wxuser_id):
        ret = yield self.user_wx_user_ds.get_wxuser({
            "id": wxuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def create_user_wx_user_ent(self, openid, unionid, wechat_id):
        wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=wechat_id)
        qx_wxuser = yield self.get_wxuser_unionid_wechat_id(
            unionid=unionid, wechat_id=settings['qx_wechat_id'])

        if wxuser:
            wxuser_id = wxuser.id
            yield self.user_wx_user_ds.update_wxuser(
                conds={
                    "id": wxuser.id
                },
                fields={
                    # "is_subscribe":   0, 如果是 update_wxuser, 则不能更新为0
                    "is_subscribe":   wxuser.is_subscribe or 0,
                    "sysuser_id":     qx_wxuser.sysuser_id,
                    "openid":         openid,
                    "nickname":       qx_wxuser.nickname,
                    "sex":            qx_wxuser.sex or 0,
                    "city":           qx_wxuser.city,
                    "country":        qx_wxuser.country,
                    "province":       qx_wxuser.province,
                    "language":       qx_wxuser.language,
                    "headimgurl":     qx_wxuser.headimgurl,
                    # "subscribe_time": curr_now(), 如果是 update_wxuser，则不需要更新 # TODO
                    "wechat_id":      wechat_id,
                    # "group_id":       0, 无用字段，可不用处理 #TODO
                    "unionid":        qx_wxuser.unionid,
                    "source":         const.WXUSER_OAUTH_UPDATE
                })

        else:
            wxuser_id = yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe":   0,
                "sysuser_id":     qx_wxuser.sysuser_id,
                "openid":         openid,
                "nickname":       qx_wxuser.nickname,
                "sex":            qx_wxuser.sex or 0,
                "city":           qx_wxuser.city,
                "country":        qx_wxuser.country,
                "province":       qx_wxuser.province,
                "language":       qx_wxuser.language,
                "headimgurl":     qx_wxuser.headimgurl,
                # "subscribe_time": curr_now(),  只是网页授权，不是关注，可不更新该字段 # TODO
                "wechat_id":      wechat_id,
                # "group_id":       0,  无用字段，可不用处理 #TODO
                "unionid":        qx_wxuser.unionid,
                "source":         const.WXUSER_OAUTH
            })

        wxuser = yield self.get_wxuser_id(wxuser_id=wxuser_id)
        raise gen.Return(wxuser)

    @gen.coroutine
    def create_qx_wxuser_by_userinfo(self, userinfo, user_id):

        qx_wechat_id = settings['qx_wechat_id']
        openid = userinfo.openid

        qx_wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=qx_wechat_id)

        if qx_wxuser and qx_wxuser.sysuser_id == user_id:
            yield self.user_wx_user_ds.update_wxuser(
                conds={"id": qx_wxuser.id},
                fields={
                    "openid":     userinfo.openid,
                    "nickname":   userinfo.nickname,
                    "sex":        userinfo.sex or 0,
                    "city":       userinfo.city,
                    "country":    userinfo.country,
                    "province":   userinfo.province,
                    "language":   userinfo.language,
                    "headimgurl": userinfo.headimgurl,
                    "unionid":    userinfo.unionid if userinfo.unionid else "",
                    "source":     const.WXUSER_OAUTH_UPDATE
                })
        else:
            yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe":   0,
                "sysuser_id":     user_id,
                "openid":         userinfo.openid,
                "nickname":       userinfo.nickname,
                "sex":            userinfo.sex or 0,
                "city":           userinfo.city,
                "country":        userinfo.country,
                "province":       userinfo.province,
                "language":       userinfo.language,
                "headimgurl":     userinfo.headimgurl,
                # "subscribe_time": curr_now(),  只是网页授权，没有关注，可不更新该字段
                "wechat_id":      qx_wechat_id,
                # "group_id":       0,  无用字段，可不更新 #TODO
                "unionid":        userinfo.unionid if userinfo.unionid else "",
                "source":         const.WXUSER_OAUTH
            })

    @gen.coroutine
    def update_user_user(self, sysuser_id, data):
        response = yield self.user_user_ds.update_user(
            conds={'id': sysuser_id},
            fields={
                'name': data.name,
                'company': data.company,
                'position': data.position
        })
        raise gen.Return(response)

    @gen.coroutine
    def bind_wx_mobile(self, params, app_id):
        """
        通过基础服务对手机号和微信号进行绑定
        reference: https://wiki.moseeker.com/user_account_api.md
        point: 1
        :param params: 基本信息
        :param app_id: 请求来源
        :return: 绑定的user_id
        """
        req = ObjectDict({
            'appid': app_id,
            'unionid': params.unionid,
            'mobile': params.mobile,
        })
        try:
            user_id = yield http_post(self._ROUTE.bind_wx_mobile, req)
        except Exception as error:
            self.logger.warn(error)
            user_id = None

        raise gen.Return(user_id)

