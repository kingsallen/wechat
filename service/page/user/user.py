# coding=utf-8

from datetime import datetime

import tornado.gen as gen

import conf.common as const
from service.page.base import PageService
from setting import settings

class UserPageService(PageService):

    def __init__(self):
        super().__init__()

    @gen.coroutine
    def create_user_user(self, userinfo, wechat_id, remote_ip, source):
        """
        根据微信授权得到的 userinfo 创建 user_user
        :param userinfo:
        :param wechat_id:
        :param remote_ip:
        :param source:
        """
        # 查询 这个 unionid 是不是已经存在
        user_record = yield self.user_user_ds.get_user({
            "unionid":  userinfo.unionid,
            "parentid": 0  # 保证查找正常的 user record
        })

        # 如果存在，返回 userid
        if user_record:
            user_id = user_record.id
        else:
            # 如果不存在，创建 user_user 记录，返回 user_id
            user_id = yield self.user_user_ds.create_user({
                "username":         userinfo.unionid,
                "password":         "",
                "register_time":    datetime.now(),
                "register_ip":      remote_ip,
                "mobile":           0,
                "national_code_id": 1,
                "wechat_id":        wechat_id,
                "last_login_time":  datetime.now(),
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
    def get_user_user(self, params):
        """
        根据参数，查找 user_user
        Usage:
            get_user_user({
                'id': id,
                'unionid': unionid,
                'mobile': mobile
            })
        :param params:
        :return: dict()
        """

        ret = yield self.user_user_ds.get_user(params)
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_openid_wechat_id(self, openid, wechat_id):
        """根据 openid 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "openid":    openid
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_sysuser_id_wechat_id(self, sysuser_id, wechat_id):
        """根据 sysuer_id 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id":  wechat_id,
            "sysuser_id": sysuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_unionid_wechat_id(self, unionid, wechat_id, fields=None):
        """根据 unionid 和 wechat_id 获取 wxuser"""
        ret = yield self.user_wx_user_ds.get_wxuser({
            "wechat_id": wechat_id,
            "unionid":   unionid
        }, fields=fields)
        raise gen.Return(ret)

    @gen.coroutine
    def get_wxuser_id(self, wxuser_id):
        """根据 id 获取 wxuser """
        ret = yield self.user_wx_user_ds.get_wxuser({
            "id": wxuser_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def create_user_wx_user_ent(self, openid, unionid, wechat_id):
        """根据 unionid 创建 企业号微信用户信息"""

        wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=wechat_id)
        qx_wxuser = yield self.get_wxuser_unionid_wechat_id(
            unionid=unionid, wechat_id=settings['qx_wechat_id'])

        self.logger.debug("create_user_wx_user_ent, wxuser openid:{} wechat_id:{}".format(openid, wechat_id))
        self.logger.debug("create_user_wx_user_ent, wxuser:{}".format(wxuser))
        self.logger.debug("create_user_wx_user_ent, qx_wxuser unionid:{} wechat_id:{}".format(unionid, wechat_id))
        self.logger.debug("create_user_wx_user_ent, qx_wxuser:{}".format(qx_wxuser))

        if wxuser:
            wxuser_id = wxuser.id
            yield self.user_wx_user_ds.update_wxuser(
                conds={
                    "id": wxuser.id
                },
                fields={
                    "is_subscribe": wxuser.is_subscribe or 0,
                    "sysuser_id":   qx_wxuser.sysuser_id,
                    "openid":       openid,
                    "nickname":     qx_wxuser.nickname,
                    "sex":          qx_wxuser.sex or 0,
                    "city":         qx_wxuser.city,
                    "country":      qx_wxuser.country,
                    "province":     qx_wxuser.province,
                    "language":     qx_wxuser.language,
                    "headimgurl":   qx_wxuser.headimgurl,
                    "wechat_id":    wechat_id,
                    "unionid":      qx_wxuser.unionid,
                    "source":       const.WX_USER_SOURCE_OAUTH_UPDATE
                })

        else:
            wxuser_id = yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe": 0,
                "sysuser_id":   qx_wxuser.sysuser_id,
                "openid":       openid,
                "nickname":     qx_wxuser.nickname,
                "sex":          qx_wxuser.sex or 0,
                "city":         qx_wxuser.city,
                "country":      qx_wxuser.country,
                "province":     qx_wxuser.province,
                "language":     qx_wxuser.language,
                "headimgurl":   qx_wxuser.headimgurl,
                "wechat_id":    wechat_id,
                "unionid":      qx_wxuser.unionid,
                "source":       const.WX_USER_SOURCE_OAUTH
            })

        wxuser = yield self.get_wxuser_id(wxuser_id=wxuser_id)
        raise gen.Return(wxuser)

    @gen.coroutine
    def create_qx_wxuser_by_userinfo(self, userinfo, user_id):
        """从微信授权的 userinfo 创建 qx user"""
        qx_wechat_id = settings['qx_wechat_id']
        openid = userinfo.openid

        qx_wxuser = yield self.get_wxuser_openid_wechat_id(
            openid=openid, wechat_id=qx_wechat_id)

        self.logger.debug("create_qx_wxuser_by_userinfo, qx_wxuser:{}".format(qx_wxuser))

        # 如果 qx_wxuser.sysuser_id = 0 表示只关注过，但是没有打开过页面
        if qx_wxuser and (qx_wxuser.sysuser_id == 0 or qx_wxuser.sysuser_id == user_id):
            yield self.user_wx_user_ds.update_wxuser(
                conds={"id": qx_wxuser.id},
                fields={
                    "sysuser_id": user_id,
                    "openid":     userinfo.openid,
                    "nickname":   userinfo.nickname,
                    "sex":        userinfo.sex or 0,
                    "city":       userinfo.city,
                    "country":    userinfo.country,
                    "province":   userinfo.province,
                    "language":   userinfo.language,
                    "headimgurl": userinfo.headimgurl,
                    "unionid":    userinfo.unionid if userinfo.unionid else "",
                    "source":     const.WX_USER_SOURCE_OAUTH_UPDATE
                })
        else:
            yield self.user_wx_user_ds.create_wxuser({
                "is_subscribe": 0,
                "sysuser_id":   user_id,
                "openid":       userinfo.openid,
                "nickname":     userinfo.nickname,
                "sex":          userinfo.sex or 0,
                "city":         userinfo.city,
                "country":      userinfo.country,
                "province":     userinfo.province,
                "language":     userinfo.language,
                "headimgurl":   userinfo.headimgurl,
                "wechat_id":    qx_wechat_id,
                "unionid":      userinfo.unionid if userinfo.unionid else "",
                "source":       const.WX_USER_SOURCE_OAUTH
            })

    @gen.coroutine
    def ensure_user_unionid(self, user_id, unionid):
        user = yield self.user_user_ds.get_user(
            conds={'id': user_id},
            fields=['unionid']
        )
        if user.unionid != unionid:
            self.logger.warning("user_user.unionid incorrect, user:{}, real_unionid: {}".format(user, unionid))
            yield self.user_user_ds.update_user(
                conds={'id': user_id},
                fields={'unionid': unionid}
            )
            self.logger.warning("fixed")

    @gen.coroutine
    def update_user_user_current_info(self, sysuser_id, data):
        """更新用户真实姓名，最近工作单位和最近职位"""
        response = yield self.user_user_ds.update_user(
            conds={'id': sysuser_id},
            fields={
                'name':     data.name,
                'company':  data.company,
                'position': data.position
            })
        raise gen.Return(response)

    @gen.coroutine
    def bind_mobile(self, user_id, mobile):
        """用户手机号绑定操作，更新 username 为手机号"""
        yield self.user_user_ds.update_user(
            conds={
                'id': user_id
            },
            fields={
                'mobile':   int(mobile),
                'username': str(mobile)
            })

    @gen.coroutine
    def get_valid_employee_by_user_id(self, user_id, company_id):
        ret = yield self.user_employee_ds.get_employee({
            "sysuser_id": user_id,
            "disable":    const.OLD_YES,
            "activation": const.OLD_YES,
            "company_id": company_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def get_employee_cert_conf(self, company_id):
        ret = yield self.hr_employee_cert_conf_ds.get_employee_cert_conf({
            "company_id": company_id
        })
        raise gen.Return(ret)

    @gen.coroutine
    def favorite_position(self, current_user, pid):
        """用户收藏职位的粒子操作
        :param current_user: user session 信息
        :param pid: 职位id
        """

        position_fav = yield self._get_user_favorite_records(
            current_user.sysuser.id, pid)

        # 没有数据时
        if not position_fav:
            fields = {
                "position_id": pid,
                "sysuser_id":  current_user.sysuser.id,
                "favorite":    const.FAV_YES,
                "wxuser_id":   current_user.wxuser.id or 0
            }
            if current_user.recom:
                fields.update({
                    "recom_id": current_user.recom.id
                })
            inserted_id = yield self.user_fav_position_ds.insert_user_fav_position(fields)
            raise gen.Return(bool(inserted_id))

        # 有数据时
        else:
            position_fav = position_fav[0]

            # 如果已经收藏，则不作任何操作
            if position_fav.favorite == const.FAV_YES:
                self.logger.warning(
                    "User already favorited the position. "
                    "user_id: {}, pid: {}".format(current_user.sysuser.id,
                                                  pid))
                ret = True
            else:
                # 变更 favorite 为 FAV_YES
                ret = self.user_fav_position_ds.update_user_fav_position(
                    fields={
                        "favorite": const.FAV_YES
                    },
                    conds={
                        "id": position_fav.id
                    }
                )
            raise gen.Return(ret)

    @gen.coroutine
    def unfavorite_position(self, current_user, pid):
        """用户取消收藏职位的粒子操作
        :param current_user: user session 信息
        :param pid: 职位id
        """
        position_fav = yield self._get_user_favorite_records(
            current_user.sysuser.id, pid)

        # 没有数据时, 不做任何操作
        if not position_fav:
            self.logger.warning(
                "Cannot unfavorite the position because user hasn't "
                "favorited it. "
                "user_id: {}, pid: {}".format(current_user.sysuser.id, pid))
            raise gen.Return(True)

        # 有数据时
        else:
            position_fav = position_fav[0]

            # 如果已经取消收藏，则不作任何操作
            if position_fav.favorite == const.FAV_NO:
                self.logger.warning(
                    "User already unfavorited the position. user_id: {}, "
                    "pid: {}".format(
                        current_user.sysuser.id, pid))
                ret = True
            else:
                # 变更 favorite 为 FAV_NO
                ret = self.user_fav_position_ds.update_user_fav_position(
                    fields={
                        "favorite": const.FAV_NO
                    },
                    conds={
                        "id": position_fav.id
                    }
                )
            raise gen.Return(ret)

    @gen.coroutine
    def _get_user_favorite_records(self, user_id, pid):
        """获取用户收藏职位信息
        :param user_id:
        :param pid:
        :return: list
        """
        position_fav = yield \
            self.user_fav_position_ds.get_user_fav_position_list({
                "position_id": pid,
                "sysuser_id":  user_id
            })
        # filter 数据，应该有 0 条或 1 条数据
        position_fav = [p for p in position_fav if
                        p.favorite in (const.FAV_YES, const.FAV_NO)]
        raise gen.Return(position_fav)
