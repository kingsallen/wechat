# coding=utf-8

import tornado.gen as gen

from service.page.base import PageService
from util.tool.date_tool import curr_now
import conf.common as const

from setting import settings


class UserPageService(PageService):

    def __init__(self, logger):
        super().__init__(logger)

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
                "username": userinfo.unionid,
                "password": "",
                "register_time": curr_now(),
                "register_ip": remote_ip,
                "mobile": 0,
                "national_code_id": 1,
                "wechat_id": wechat_id,
                "last_login_time": curr_now(),
                "last_login_ip": remote_ip,
                "login_count": 1,
                "unionid": userinfo.unionid,
                "source": source,
                "nickname": userinfo.nickname,
                "name": "",
                "headimg": userinfo.headimgurl,
            })

            assert user_id
            yield self.user_settings_ds.create_user_settings({
                "user_id": user_id
            })

        raise gen.Return(user_id)

    @gen.coroutine
    def get_user_user(self, unionid=None):
        ret = self.user_user_ds.get_user({
            "unionid": unionid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser(self, openid, wechat_id):
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "openid":    openid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser(self, unionid, wechat_id):
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "unionid":    unionid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser(self, wxuser_id):
        ret = yield self.user_wx_user_ds.get_wxuser({
            "id": wxuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def create_user_wx_user_ent(self, openid, unionid, wechat_id):
        wxuser_id = 0
        wxuser = yield self.get_wxuser(openid=openid, wechat_id=wechat_id)
        qx_wxuser = yield self.get_wxuser(unionid=unionid, wechat_id=settings[
            'qx_wechat_id'])

        if wxuser:
            wxuser_id = wxuser.id
            yield self.user_wx_user_ds.update_wxuser(
                conds={
                    "id": wxuser.id
                },
                fields={
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
                    "subscribe_time": curr_now(),
                    "wechat_id":      wechat_id,
                    "group_id":       0,
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
                "subscribe_time": curr_now(),
                "wechat_id":      wechat_id,
                "group_id":       0,
                "unionid":        qx_wxuser.unionid,
                "source":         const.WXUSER_OAUTH
            })

        wxuser = yield self.get_wxuser(wxuser_id=wxuser_id)
        raise gen.Return(wxuser)

    @gen.coroutine
    def create_qx_wxuser_by_userinfo(self, userinfo, user_id):

        qx_wechat_id = settings['qx_wechat_id']
        openid = userinfo.openid

        qx_wxuser = yield self.get_wxuser(openid=openid, wechat_id=qx_wechat_id)

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
                "is_subscribe": 0,
                "sysuser_id": user_id,
                "openid": userinfo.openid,
                "nickname": userinfo.nickname,
                "sex": userinfo.sex or 0,
                "city": userinfo.city,
                "country": userinfo.country,
                "province": userinfo.province,
                "language": userinfo.language,
                "headimgurl": userinfo.headimgurl,
                "subscribe_time": curr_now(),
                "wechat_id": qx_wechat_id,
                "group_id": 0,
                "unionid": userinfo.unionid if userinfo.unionid else "",
                "source": const.WXUSER_OAUTH
            })
